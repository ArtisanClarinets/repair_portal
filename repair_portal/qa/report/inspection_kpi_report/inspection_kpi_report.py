# File: repair_portal/qa/report/inspection_kpi_report/inspection_kpi_report.py
# Updated: 2025-06-27
# Version: 1.0
# Purpose: Script Report for KPI/trend analysis of inspection outcomes (QA, repair, etc)


import frappe


def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	inspection_type = filters.get("inspection_type")

	conditions = []
	params = {}
	if from_date:
		conditions.append("inspection_date >= %(from_date)s")
		params["from_date"] = from_date
	if to_date:
		conditions.append("inspection_date <= %(to_date)s")
		params["to_date"] = to_date
	if inspection_type:
		conditions.append("inspection_type = %(inspection_type)s")
		params["inspection_type"] = inspection_type
	where_clause = " AND ".join(conditions) if conditions else "1=1"

	inspections = frappe.db.sql(
		f"""
        SELECT name, inspection_type, status
        FROM `tabInspection Report`
        WHERE {where_clause}
    """,
		params,
		as_dict=True,
	)

	# Metrics
	total = len(inspections)
	first_pass_yield = 0
	passed = [i for i in inspections if i.status == "Passed"]
	first_pass_yield = (len(passed) / total) * 100 if total else 0

	# Avg ΔP and spring-tension spread (from checklist)
	dp_sum, dp_count, spread_sum, spread_count = 0, 0, 0, 0
	re_service_count = 0
	for i in inspections:
		checklists = frappe.db.get_all(
			"Inspection Checklist Item",
			filters={"parent": i["name"]},
			fields=["criteria", "value", "area"],
		)
		for c in checklists:
			if "ΔP" in c["criteria"] or "Delta P" in c["criteria"] or "pressure" in c["criteria"]:
				try:
					dp = float(c["value"].replace("psi", "").strip()) if c["value"] else None
					if dp is not None:
						dp_sum += dp
						dp_count += 1
				except Exception:
					pass
			if "spring" in c["area"].lower() and "spread" in c["criteria"].lower():
				try:
					spread = float(c["value"].replace("g", "").strip()) if c["value"] else None
					if spread is not None:
						spread_sum += spread
						spread_count += 1
				except Exception:
					pass
		# Find any re-service by checking if the same instrument_id has another inspection within 180 days
		instr_id = frappe.db.get_value("Inspection Report", i["name"], "instrument_id")
		recent = frappe.db.sql(
			"""
            SELECT COUNT(*) FROM `tabInspection Report`
            WHERE instrument_id = %s AND name != %s AND ABS(DATEDIFF(inspection_date, (SELECT inspection_date FROM `tabInspection Report` WHERE name = %s))) <= 180
        """,
			(instr_id, i["name"], i["name"]),
		)
		if recent and recent[0][0] > 0:
			re_service_count += 1

	avg_dp = (dp_sum / dp_count) if dp_count else 0
	avg_spring_spread = (spread_sum / spread_count) if spread_count else 0
	re_service_rate = (re_service_count / total) * 100 if total else 0

	row = {
		"inspection_type": inspection_type or "All",
		"total": total,
		"first_pass_yield": round(first_pass_yield, 2),
		"avg_dp": round(avg_dp, 3),
		"avg_spring_spread": round(avg_spring_spread, 2),
		"re_service_rate": round(re_service_rate, 2),
	}
	columns = [
		{
			"label": "Inspection Type",
			"fieldname": "inspection_type",
			"fieldtype": "Data",
			"width": 120,
		},
		{"label": "Total Inspections", "fieldname": "total", "fieldtype": "Int", "width": 120},
		{
			"label": "First Pass Yield (%)",
			"fieldname": "first_pass_yield",
			"fieldtype": "Percent",
			"width": 150,
		},
		{"label": "Average ΔP (psi)", "fieldname": "avg_dp", "fieldtype": "Float", "width": 120},
		{
			"label": "Avg Spring Spread (g)",
			"fieldname": "avg_spring_spread",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": "Re-service Rate (%)",
			"fieldname": "re_service_rate",
			"fieldtype": "Percent",
			"width": 150,
		},
	]
	return columns, [row]
