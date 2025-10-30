"""Material planning and stock integration for Repair Orders."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import frappe
from frappe import _
from frappe.utils import flt, nowdate

OPEN_STATES = {
    "Requested",
    "Awaiting Arrival",
    "Checked-In",
    "Quoted",
    "Approved",
    "In Progress",
    "QC",
    "Ready to Ship",
}


@dataclass
class ShortItem:
    rowname: str
    item_code: str
    warehouse: str
    shortage_qty: float
    uom: str | None


def _get_company(doc: frappe.Document) -> str:
    return (
        doc.get("company")
        or frappe.defaults.get_user_default("Company")
        or frappe.defaults.get_global_default("company")
    )


def _get_default_warehouse(doc: frappe.Document) -> str | None:
    try:
        settings = frappe.get_single("Repair Settings")
        return settings.get("default_source_warehouse")
    except Exception:
        return None


def _fetch_template(repair_class: str | None, instrument: str | None) -> frappe._dict | None:
    filters = {}
    if repair_class:
        filters["repair_class"] = repair_class
    templates = frappe.get_all(
        "Clarinet BOM Template",
        filters=filters,
        fields=["name", "instrument_model"],
        order_by="modified desc",
    )
    if not templates:
        return None
    if instrument:
        inst_model = frappe.db.get_value("Instrument", instrument, "model")
        for candidate in templates:
            if candidate.instrument_model and inst_model and candidate.instrument_model == inst_model:
                return frappe.get_doc("Clarinet BOM Template", candidate.name)
    return frappe.get_doc("Clarinet BOM Template", templates[0].name)


def _planned_items_exist(doc: frappe.Document) -> bool:
    return any(row.get("item") for row in doc.get("planned_materials") or [])


def before_submit(doc: frappe.Document, _event: str | None = None) -> None:
    """Populate planned materials from a template prior to submit."""
    if _planned_items_exist(doc):
        return

    template = _fetch_template(doc.get("repair_class"), doc.get("instrument"))
    if not template:
        return

    default_wh = _get_default_warehouse(doc)
    for line in template.get("lines") or []:
        doc.append(
            "planned_materials",
            {
                "item": line.item,
                "qty": line.qty,
                "uom": line.uom,
                "description": frappe.db.get_value("Item", line.item, "item_name"),
                "warehouse": default_wh,
                "service_type": line.get("service_type"),
                "vendor": line.get("vendor"),
                "lead_time_days": line.get("lead_time_days"),
            },
        )


def _collect_shortages(doc: frappe.Document) -> list[ShortItem]:
    default_wh = _get_default_warehouse(doc)
    shortages: list[ShortItem] = []
    for row in doc.get("planned_materials") or []:
        item = (row.get("item") or "").strip()
        if not item:
            continue
        warehouse = (row.get("warehouse") or default_wh or "").strip()
        if not warehouse:
            continue
        qty = flt(row.get("qty") or 0)
        if qty <= 0:
            continue
        available = flt(
            frappe.db.get_value("Bin", {"item_code": item, "warehouse": warehouse}, "projected_qty") or 0
        )
        if available < qty:
            shortages.append(
                ShortItem(
                    rowname=row.name,
                    item_code=item,
                    warehouse=warehouse,
                    shortage_qty=qty - available,
                    uom=row.get("uom"),
                )
            )
    return shortages


def _create_material_request(doc: frappe.Document, shortages: list[ShortItem], request_type: str) -> str:
    mr = frappe.new_doc("Material Request")
    mr.material_request_type = request_type
    mr.company = _get_company(doc)
    mr.schedule_date = nowdate()
    mr.set_title(_(f"{request_type} for {doc.name}"))
    for short in shortages:
        mr.append(
            "items",
            {
                "item_code": short.item_code,
                "qty": short.shortage_qty,
                "schedule_date": nowdate(),
                "warehouse": short.warehouse,
                "uom": short.uom,
                "conversion_factor": 1,
            },
        )
    mr.insert(ignore_permissions=True)
    mr.submit()
    return mr.name


def _link_rows_to_request(
    rows: Iterable[ShortItem],
    fieldname: str,
    request_name: str,
    request_type: str | None = None,
) -> None:
    for row in rows:
        values: dict[str, str] = {fieldname: request_name}
        if fieldname == "reservation_entry" and request_type:
            values["reservation_entry_type"] = request_type
        frappe.db.set_value("Planned Material", row.rowname, values)


def _log_vendor_events(doc: frappe.Document) -> None:
    for row in doc.get("planned_materials") or []:
        if (row.get("service_type") or "").lower() != "plating":
            continue
        vendor = row.get("vendor")
        if not vendor:
            continue
        log = frappe.get_doc(
            {
                "doctype": "Vendor Turnaround Log",
                "vendor": vendor,
                "service_type": "Plating",
                "avg_days": row.get("lead_time_days") or 0,
                "last_order_date": nowdate(),
                "notes": _(f"Auto-created from Repair Order {doc.name}"),
            }
        )
        log.insert(ignore_permissions=True)


def on_submit(doc: frappe.Document, _event: str | None = None) -> None:
    shortages = _collect_shortages(doc)
    if shortages:
        mr_name = _create_material_request(doc, shortages, "Purchase")
        _link_rows_to_request(shortages, "material_request", mr_name)
    _log_vendor_events(doc)


@frappe.whitelist()
def reserve_stock(repair_order: str) -> dict[str, str]:
    doc = frappe.get_doc("Repair Order", repair_order)
    doc.check_permission("write")
    rows = [
        ShortItem(row.name, row.item, row.warehouse, flt(row.qty), row.get("uom"))
        for row in doc.get("planned_materials") or []
        if row.item and not row.get("reservation_entry")
    ]
    if not rows:
        return {"status": "noop"}
    mr_name = _create_material_request(doc, rows, "Material Transfer")
    _link_rows_to_request(rows, "reservation_entry", mr_name, "Material Request")
    frappe.msgprint(_("Created reservation request {0}").format(mr_name))
    return {"status": "reserved", "material_request": mr_name}


@frappe.whitelist()
def issue_to_job(repair_order: str) -> dict[str, str]:
    doc = frappe.get_doc("Repair Order", repair_order)
    doc.check_permission("write")
    if doc.workflow_state and doc.workflow_state not in OPEN_STATES:
        frappe.throw(_("Repair Order {0} is not in an issuable state.").format(doc.name))

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.purpose = "Material Issue"
    stock_entry.company = _get_company(doc)
    for row in doc.get("planned_materials") or []:
        if not row.item or flt(row.qty) <= 0:
            continue
        stock_entry.append(
            "items",
            {
                "item_code": row.item,
                "qty": flt(row.qty),
                "s_warehouse": row.warehouse or _get_default_warehouse(doc),
                "uom": row.get("uom") or frappe.db.get_value("Item", row.item, "stock_uom"),
                "conversion_factor": 1,
            },
        )
    if not stock_entry.get("items"):
        frappe.throw(_("No planned materials available to issue."))
    stock_entry.insert(ignore_permissions=True)
    stock_entry.submit()

    for item in stock_entry.items:
        frappe.get_doc(
            {
                "doctype": "Actual Material",
                "parenttype": "Repair Order",
                "parentfield": "actual_materials",
                "parent": doc.name,
                "item": item.item_code,
                "qty": item.qty,
                "uom": item.uom,
                "warehouse": item.s_warehouse,
                "valuation_rate": flt(item.valuation_rate),
                "stock_entry": stock_entry.name,
            }
        ).insert(ignore_permissions=True)
    frappe.msgprint(_("Issued materials via Stock Entry {0}").format(stock_entry.name))
    return {"status": "issued", "stock_entry": stock_entry.name}
