# File: repair_portal/repair/report/technician_utilization/technician_utilization.py
# Updated: 2025-06-15
# Version: 1.0
# Purpose: Calculates total hours per technician from Repair Tasks

import frappe


def execute(filters=None):
	conditions = []
	if filters.get("from_date"):
		conditions.append(f"creation >= '{filters['from_date']}'")
	if filters.get("to_date"):
		conditions.append(f"creation <= '{filters['to_date']}'")

	where_clause = f'WHERE {" AND ".join(conditions)}' if conditions else ""

	data = frappe.db.sql(
		f"""
        SELECT
            technician,
            SUM(actual_hours) AS total_hours,
            COUNT(name) AS task_count
        FROM `tabRepair Task`
        {where_clause}
        GROUP BY technician
    """,
		as_dict=True,
	)

	columns = [
		{"label": "Technician", "fieldname": "technician", "fieldtype": "Link", "options": "User"},
		{"label": "Total Hours", "fieldname": "total_hours", "fieldtype": "Float"},
		{"label": "Tasks Completed", "fieldname": "task_count", "fieldtype": "Int"},
	]

	return columns, data
