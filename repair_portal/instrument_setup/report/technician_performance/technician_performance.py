import frappe


def execute(filters=None):
    columns = [
        {
            "label": "Technician",
            "fieldname": "technician",
            "fieldtype": "Link",
            "options": "User",
            "width": 180,
        },
        {"label": "Total Setups", "fieldname": "total", "fieldtype": "Int"},
        {"label": "Pass Rate (%)", "fieldname": "pass_rate", "fieldtype": "Percent"},
        {"label": "Average Hours", "fieldname": "avg_hours", "fieldtype": "Float"},
    ]

    data = frappe.db.sql(
        """
        SELECT
            technician,
            COUNT(name) as total,
            SUM(CASE WHEN status = 'Pass' THEN 1 ELSE 0 END) * 100.0 / COUNT(name) as pass_rate,
            AVG(labor_hours) as avg_hours
        FROM `tabClarinet Initial Setup`
        GROUP BY technician
    """,
        as_dict=True,
    )

    return columns, data
