# repair_portal/instrument_profile/page/instrument_history/instrument_history.py
# Updated: 2025-06-15
# Version: 1.1
# Purpose: Backend data aggregator for customer instrument portal view

import frappe


def get_context(context):
    pass  # Required for Frappe Page loading


def get_instrument_data(instrument_profile):
    profile = frappe.get_doc("Instrument Profile", instrument_profile)

    repair_logs = frappe.get_all(
        "Repair Task Log",
        filters={"instrument_profile": instrument_profile},
        fields=["date", "status", "notes"],
        order_by="date desc",
    )

    external_logs = frappe.get_all(
        "Customer External Work Log",
        filters={"instrument_profile": instrument_profile},
        fields=["service_date", "service_type", "external_shop_name", "service_notes"],
    )

    return {"profile": profile, "repair_logs": repair_logs, "external_logs": external_logs}
