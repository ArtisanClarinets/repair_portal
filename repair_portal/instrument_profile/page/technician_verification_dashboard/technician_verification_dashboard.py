# Path: instrument_profile/page/technician_verification_dashboard/technician_verification_dashboard.py
# Date: 2025-06-15
# Version: 1.0
# Purpose: Backend logic for Technician Verification Dashboard - listing and verifying client-submitted instruments

import frappe
from frappe.utils import now


def get_pending_profiles():
    return frappe.get_all(
        "Instrument Profile",
        filters={"is_verified": 0, "submitted_by_client": 1},
        fields=["name", "client", "status"],
    )


def verify_instrument(name):
    doc = frappe.get_doc("Instrument Profile", name)
    doc.is_verified = 1
    doc.verified_by = frappe.session.user
    doc.verified_on = now()
    doc.save()
    frappe.db.commit()
