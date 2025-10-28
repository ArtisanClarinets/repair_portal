"""Point-of-sale hooks for contextual upsell suggestions."""
from __future__ import annotations

import frappe
from frappe import _


def _gather_upsell_items(repair_class: str) -> list[dict[str, str | float]]:
    if not repair_class:
        return []
    rows = frappe.get_all(
        "Class Upsell",
        filters={"parent": repair_class},
        fields=["item", "price", "description"],
        order_by="idx asc",
    )
    return [row for row in rows if row.item]


def _sales_invoice_contains_item(doc: frappe.Document, item_code: str) -> bool:
    return any((row.item_code or "").strip() == item_code for row in doc.get("items", []))


def suggest_repair_class_upsells(doc: frappe.Document, _event: str | None = None) -> None:
    """Display targeted upsell hints when the invoice references a repair order."""
    repair_order = (doc.get("repair_order") or doc.get("repair_order_reference") or "").strip()
    if not repair_order:
        return

    try:
        order = frappe.get_doc("Repair Order", repair_order)
    except frappe.DoesNotExistError:
        return

    if not frappe.has_permission(order.doctype, "read", doc=order):
        return

    repair_class = order.get("repair_class")
    upsells = _gather_upsell_items(repair_class)
    if not upsells:
        return

    missing: list[str] = []
    for row in upsells:
        if not _sales_invoice_contains_item(doc, row["item"]):
            label = frappe.get_cached_value("Item", row["item"], "item_name") or row["item"]
            price = row.get("price")
            if price:
                missing.append(_("{0} ({1})" ).format(label, frappe.utils.fmt_money(price)))
            else:
                missing.append(label)

    if not missing:
        return

    frappe.msgprint(
        _("Consider adding these upsells from the {0} package: {1}").format(
            frappe.bold(repair_class or order.repair_class), ", ".join(missing)
        ),
        indicator="orange",
        alert=True,
    )
