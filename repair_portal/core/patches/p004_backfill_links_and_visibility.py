"""Backfill cross-module links and portal visibility defaults."""

from __future__ import annotations

import frappe


def _ensure_boolean_default(doctype: str, field: str, default: int) -> None:
    if not frappe.db.table_exists(doctype):
        return
    frappe.db.sql(f"update `tab{doctype}` set {field} = %s where {field} is null", (default,))


def _backfill_repair_order_links() -> None:
    if not frappe.db.table_exists("Repair Order"):
        return
    rows = frappe.db.get_all(
        "Repair Order",
        fields=["name", "player_profile", "customer"],
        filters={"player_profile": ("is", "set"), "customer": ("is", "not set")},
    )
    for row in rows:
        customer = frappe.db.get_value("Player Profile", row["player_profile"], "customer")
        if customer:
            frappe.db.set_value("Repair Order", row["name"], "customer", customer)


def execute() -> None:
    _ensure_boolean_default("Repair Communication", "visible_in_portal", 0)
    _ensure_boolean_default("Repair Order", "show_portal_updates", 0)
    _backfill_repair_order_links()
