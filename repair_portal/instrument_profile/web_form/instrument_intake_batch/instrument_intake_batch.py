# Path: repair_portal/instrument_profile/web_form/instrument_intake_batch/instrument_intake_batch.py
# Date: 2025-10-02
# Version: 1.1.0
# Description: Web form controller for instrument batch intake; prefills defaults and validates user context for batch creation
# Dependencies: frappe

import frappe


def get_context(context):
    """Prefill default date and user-linked supplier if present."""
    user = frappe.session.user
    if user and user != "Guest":
        default_supplier = frappe.db.get_value("Supplier", {"owner": user}, "name")
        if default_supplier:
            context.supplier = default_supplier
    context.date = frappe.utils.nowdate()  # type: ignore
    return context
