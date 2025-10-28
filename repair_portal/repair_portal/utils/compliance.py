"""Compliance automation for data retention."""
from __future__ import annotations

import frappe
from frappe.utils import add_months, nowdate


def anonymize_closed_repairs() -> None:
    """Redact sensitive fields on completed repair orders outside retention window."""
    if not frappe.db.exists("DocType", "Repair Portal Settings"):
        return
    settings = frappe.get_single("Repair Portal Settings")
    months = int(settings.data_retention_months or 0)
    if months <= 0:
        return
    cutoff = add_months(nowdate(), -months)
    orders = frappe.get_all(
        "Repair Order",
        filters={
            "workflow_state": "Completed",
            "anonymized_on": ("is", "not set"),
            "modified": ("<", cutoff),
        },
        fields=["name", "repair_request", "instrument", "customer"],
    )
    for row in orders:
        _anonymize_order(row)


def _anonymize_order(row: dict) -> None:
    frappe.db.set_value("Repair Order", row.name, {
        "barcode": None,
        "service_plan_claim": None,
        "warranty_flag": 0,
        "anonymized_on": nowdate(),
    })
    if row.repair_request and frappe.db.exists("Repair Request", row.repair_request):
        frappe.db.set_value(
            "Repair Request",
            row.repair_request,
            {
                "requested_services": None,
                "preferred_carrier": None,
                "portal_token": None,
            },
        )
    if frappe.db.exists("Instrument", row.instrument):
        frappe.db.set_value("Instrument", row.instrument, "notes", None)

