# File: repair_portal/repair_portal/enhancements/report/top_upgrade_requests/top_upgrade_requests.py
# Updated: 2025-06-12
# Version: 1.0
# Purpose: Show most requested upgrade types

import frappe


def execute(filters=None):
	data = frappe.db.sql(
		"""
        SELECT u.upgrade_description, COUNT(*) AS total
        FROM `tabCustomer Upgrade Request` r
        JOIN `tabUpgrade Option` u ON u.parent = r.name
        GROUP BY u.upgrade_description
        ORDER BY total DESC
        LIMIT 10
    """,
		as_dict=True,
	)

	columns = [
		{"fieldname": "upgrade_description", "label": "Upgrade", "fieldtype": "Data", "width": 300},
		{"fieldname": "total", "label": "Total Requested", "fieldtype": "Int", "width": 120},
	]

	return columns, data
