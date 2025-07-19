"""
File: instrument_profile/web_form/instrument_intake_batch/instrument_intake_batch.py
Updated: 2025-07-03
Version: 1.1
Purpose: Web form controller for instrument batch intake. Prefills and assists user context for batch creation.
"""

import frappe


def get_context(context):
    """Prefill default date and user-linked supplier if present."""
    user = frappe.session.user
    if user and user != "Guest":
        default_supplier = frappe.db.get_value("Supplier", {"owner": user}, "name")
        if default_supplier:
            context.supplier = default_supplier
    context.date = frappe.utils.nowdate()
    return context
