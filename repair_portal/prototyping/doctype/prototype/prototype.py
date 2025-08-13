from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe import _
from typing import List, Dict

# Safety: ensure ERPNext installed
def _assert_erpnext():
    if "erpnext" not in frappe.get_installed_apps():
        frappe.throw(_("ERPNext must be installed to use Prototyping."))

def _ensure_linked_doctype_exists(doctype: str):
    if not frappe.db.exists("DocType", doctype):
        frappe.throw(_("{0} DocType not found.").format(doctype))

class Prototype(Document):
    def validate(self):
        _assert_erpnext()
        _ensure_linked_doctype_exists("Item")
        _ensure_linked_doctype_exists("BOM")
        if not self.company:
            frappe.throw(_("Company is required."))

        # Basic sanity
        if self.target_qty and self.target_qty <= 0:
            frappe.throw(_("Target Build Qty must be > 0."))

    def on_submit(self):
        # When a Prototype is submitted with status "Ready for Build",
        # auto-create Item & BOM if missing (non-destructive if already present)
        if self.status in ("Ready for Build", "In Test", "Approved"):
            if not self.item or not self.bom:
                item_name, bom_name = make_item_and_bom(self.name)
                if item_name and not self.item:
                    self.db_set("item", item_name)
                if bom_name and not self.bom:
                    self.db_set("bom", bom_name)
                frappe.msgprint(_("Linked Item: {0}, BOM: {1}").format(self.item, self.bom))

@frappe.whitelist()
def open_designer_url(prototype: str) -> str:
    """Return route to the Prototype Designer page with this prototype."""
    frappe.only_for(("System Manager", "Manufacturing Manager", "Manufacturing User"))
    return f"/app/prototype-designer?name={frappe.utils.quote(prototype)}"

@frappe.whitelist()
def make_item_and_bom(prototype: str) -> Dict[str, str]:
    """Create a non-stock Item and a non-default BOM flagged as prototype.
       Returns {'item': <name>, 'bom': <name>}."""
    frappe.only_for(("System Manager", "Manufacturing Manager"))
    _assert_erpnext()

    doc = frappe.get_doc("Prototype", prototype)
    company = doc.company

    # 1) Create Item (non-stock, custom field to tag as prototype)
    item_name = doc.item
    if not item_name:
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": f"PRT-{doc.name}",
            "item_name": doc.title or f"Prototype {doc.name}",
            "item_group": "All Item Groups",
            "is_stock_item": 0,
            "is_sales_item": 0,
            "is_purchase_item": 0,
            "description": (doc.design_notes or "") + "\n[Auto-created by Prototype]",
            "disabled": 0,
            "maintain_serial_no": 0,
            "default_uom": doc.uom or "Nos",
        }).insert(ignore_permissions=True)
        item_name = item.name
        doc.db_set("item", item_name)

        # Set a custom flag (creates the field on the fly if you’ve added it via Customize Form)
        try:
            item.db_set("is_prototype", 1)
        except Exception:
            pass

    # 2) Create BOM (empty starter; user can add items later)
    bom_name = doc.bom
    if not bom_name:
        if not item_name:
            frappe.throw(_("Item not found/created for Prototype."))
        bom = frappe.get_doc({
            "doctype": "BOM",
            "item": item_name,
            "company": company,
            "quantity": 1,
            "is_default": 0,
            "is_active": 1,
            "with_operations": 1 if doc.routing else 0,
            "rm_cost_as_per": "Valuation Rate",
            "scrap_items": [],
            "items": [],  # You will populate via UI or custom mapping
        })
        if doc.routing:
            bom.set("operations", [{"operation": op.operation, "time_in_mins": op.time_in_mins if hasattr(op, "time_in_mins") else 0} for op in frappe.get_all("Routing Operation", filters={"parent": doc.routing}, fields=["operation","time_in_mins"])])
            bom.routing = doc.routing
        bom.insert(ignore_permissions=True)
        bom_name = bom.name
        doc.db_set("bom", bom_name)

        # Custom flag on BOM (add a custom field 'is_prototype' = Check in Customize Form)
        try:
            bom.db_set("is_prototype", 1)
        except Exception:
            pass

    frappe.db.commit()
    return {"item": item_name, "bom": bom_name}

@frappe.whitelist()
def make_work_order(prototype: str) -> str:
    """Create a draft Work Order for the prototype’s BOM."""
    frappe.only_for(("System Manager", "Manufacturing Manager"))
    _assert_erpnext()

    doc = frappe.get_doc("Prototype", prototype)
    if not doc.bom or not doc.item:
        frappe.throw(_("Create Item & BOM first."))

    wo = frappe.get_doc({
        "doctype": "Work Order",
        "company": doc.company,
        "bom_no": doc.bom,
        "production_item": doc.item,
        "qty": doc.target_qty or 1,
        "fg_warehouse": doc.fg_warehouse or None,
        "wip_warehouse": doc.wip_warehouse or None,
        "source_warehouse": doc.warehouse or None,
        "expected_start_date": frappe.utils.now(),
        "description": f"Prototype build for {doc.name}"
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    return wo.name
