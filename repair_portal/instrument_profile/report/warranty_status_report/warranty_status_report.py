# repair_portal/instrument_profile/report/warranty_status_report/warranty_status_report.py
# Updated: 2025-06-15
# Version: 1.0
# Purpose: SQL source for Warranty Status Report


def execute(filters=None):
    return [
        ['Instrument', 'Serial #', 'Owner', 'Start Date', 'End Date', 'Status'],
        frappe.db.sql(
            """
            SELECT name, serial_number, owner_name, warranty_start_date, warranty_end_date,
            CASE WHEN warranty_active = 1 THEN 'Active' ELSE 'Expired' END
            FROM `tabInstrument Profile`
            ORDER BY warranty_end_date DESC
        """,
            as_list=True,
        ),
    ]
