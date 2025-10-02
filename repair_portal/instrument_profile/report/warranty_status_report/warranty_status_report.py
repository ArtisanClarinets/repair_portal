# Path: repair_portal/instrument_profile/report/warranty_status_report/warranty_status_report.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: SQL-based report showing warranty status for all instruments with expiration tracking and active/expired indicators
# Dependencies: frappe

import frappe
from frappe import _


def execute(filters=None):
    return [
        ['Instrument', 'Serial #', 'Owner', 'Start Date', 'End Date', 'Status'],
        frappe.db.sql(
            """
            SELECT name, serial_no, owner_name, warranty_start_date, warranty_end_date,
            CASE WHEN warranty_active = 1 THEN 'Active' ELSE 'Expired' END
            FROM `tabInstrument Profile`
            ORDER BY warranty_end_date DESC
        """,
            as_list=True,
        ),
    ]
