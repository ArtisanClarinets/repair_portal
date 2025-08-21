# ---------------------------------------------------------------------------
# Report: QA Failure Rate
# File: repair_portal/qa/report/qa_failure_rate/qa_failure_rate.py
# Date Updated: 2025-07-02
# Version: v1.2
# Purpose: Adds date range, technician filters, and chart.
# ---------------------------------------------------------------------------

import frappe


def execute(filters=None):
	if filters is None:
		filters = {}

	conditions = []
	params = {}

	if filters.get("from_date"):
		conditions.append("creation >= %(from_date)s")
		params["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions.append("creation <= %(to_date)s")
		params["to_date"] = filters["to_date"]

	if filters.get("qa_technician"):
		conditions.append("qa_technician = %(qa_technician)s")
		params["qa_technician"] = filters["qa_technician"]

	where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

	qa_list = frappe.db.sql(
		f"""
        SELECT
            qa_technician,
            COUNT(name) AS total_checks,
            SUM(CASE WHEN overall_passed = 0 THEN 1 ELSE 0 END) AS failures,
            ROUND(SUM(CASE WHEN overall_passed = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(name), 2) AS failure_rate
        FROM `tabFinal QA Checklist`
        {where_clause}
        GROUP BY qa_technician
        ORDER BY failure_rate DESC
        """,
		params,
		as_dict=True,
	)

	columns = [
		{
			"fieldname": "qa_technician",
			"label": "QA Technician",
			"fieldtype": "Link",
			"options": "User",
			"width": 200,
		},
		{"fieldname": "total_checks", "label": "Total QA Checks", "fieldtype": "Int", "width": 160},
		{"fieldname": "failures", "label": "Failures", "fieldtype": "Int", "width": 100},
		{
			"fieldname": "failure_rate",
			"label": "Failure Rate (%)",
			"fieldtype": "Percent",
			"width": 140,
		},
	]

	chart = {
		"data": {
			"labels": [row["qa_technician"] for row in qa_list],
			"datasets": [
				{
					"name": "Failure Rate (%)",
					"values": [row["failure_rate"] for row in qa_list],
				}
			],
		},
		"type": "bar",
	}

	return columns, qa_list, None, chart
