# relative path: repair_portal/instrument_profile/report/pending_client_instruments/pending_client_instruments.py
# updated: 2025-06-15
# version: 1.0.0
# purpose: Query report for technician review of client-submitted instruments
import frappe


def execute(filters=None):
    return [
        ['Instrument', 'Model', 'Owner', 'Verification Status'],
        frappe.db.sql("""
            SELECT
                name,
                instrument_model,
                owner,
                verification_status
            FROM `tabClient Instrument Profile`
            WHERE verification_status = 'Pending'
        """),
    ]
