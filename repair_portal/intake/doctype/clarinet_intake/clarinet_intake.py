# File Header Template
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-20
# Version: v3.7
# Purpose: Controller logic for Clarinet Intake. Fully settings-driven: all key config (warehouse, price lists, group, brand, labels, automation) now comes from Clarinet Intake Settings. Instrument is now auto-created if serial number is not found.
# Dependencies: ERPNext Item, Item Price, Serial No, Instrument, Instrument Inspection, Clarinet Initial Setup, Clarinet Intake Settings

from __future__ import annotations

from typing import Literal
import frappe
from frappe import _
from frappe.model import naming
from frappe.model.document import Document
from repair_portal.intake.doctype.clarinet_intake_settings.clarinet_intake_settings import get_intake_settings
import json

MANDATORY_BY_TYPE = {
    "New Inventory": {"body_material", "acquisition_source", "acquisition_cost", "store_asking_price", "item_code", "item_name"},
    "Repair": {"customers_stated_issue", "service_type_requested", "customer"},
    "Maintenance": {"customers_stated_issue", "service_type_requested", "customer"},
}

class ClarinetIntake(Document):
    """Business logic & validation for the Clarinet Intake document. Now fully settings-driven!"""
    name: str
    intake_record_id: str
    instrument_unique_id: str | None
    customer: str | None
    intake_type: Literal["New Inventory", "Repair", "Maintenance"]
    service_type_requested: str | None
    customers_stated_issue: str | None
    manufacturer: str | None
    model: str | None
    serial_no: str | None
    clarinet_type: str | None
    body_material: str | None
    year_of_manufacture: int | None
    acquisition_source: str | None
    acquisition_cost: float
    store_asking_price: float
    item_code: str | None
    item_name: str | None

    def autoname(self) -> None:
        settings = get_intake_settings()
        if not self.intake_record_id:
            pattern = settings.get("intake_naming_series") or "INV-#####"
            self.intake_record_id = naming.make_autoname(pattern)
        self.name = self.intake_record_id

    def validate(self) -> None:
        self._enforce_dynamic_mandatory_fields()
        self._sync_instrument_from_serial()

    def on_submit(self) -> None:
        settings = get_intake_settings()
        # All logic is now settings-driven
        if self.intake_type == "New Inventory":
            try:
                item = self._ensure_erpnext_item(settings)
                if settings.get("buying_price_list") and settings.get("selling_price_list"):
                    self._ensure_item_prices(item, settings)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), _("Item creation/price failed"))
                frappe.throw(_(f"Failed to create Item/Prices: {e}"))
        # Instrument Inspection if required
        if settings.get("require_inspection", 1):
            try:
                self._ensure_instrument_inspection(settings)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), _("Instrument Inspection creation failed"))
                frappe.throw(_(f"Failed to create Instrument Inspection: {e}"))
        # Initial Setup toggle
        if self.intake_type == "New Inventory" and settings.get("auto_create_initial_setup", 1):
            try:
                self._ensure_clarinet_initial_setup()
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), _("Clarinet Initial Setup failed"))
                frappe.msgprint(_(f"Warning: Initial Setup could not be created: {e}"))
        # Stock validation & notification
        if settings.get("notify_on_stock_issue", 1):
            try:
                self._validate_stock_in_inspection_warehouse(settings)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), _("Stock Validation failed"))
                frappe.msgprint(_(f"Warning: Stock validation error: {e}"))

    def _ensure_erpnext_item(self, settings):
        item = frappe.db.exists("Item", {"item_code": self.item_code})
        doc = frappe.get_doc("Item", item) if item else frappe.new_doc("Item")
        # Brand mapping via settings (optional JSON)
        brand = self.manufacturer or "Unknown"
        try:
            mapping = json.loads(settings.get("brand_mapping", "{}"))
            brand = mapping.get(brand, brand)
        except Exception:
            pass
        supplier_code = (settings.get("supplier_code_prefix") or "") + (self.item_code or "")
        doc.item_code = self.item_code
        doc.item_name = self.item_name
        doc.item_group = settings.get("default_item_group") or "Clarinets"
        doc.brand = brand
        doc.default_warehouse = settings.get("default_inspection_warehouse") or "Clarinet Inspection"
        doc.supplier_code = supplier_code
        doc.stock_uom = settings.get("stock_uom") or "Nos"
        doc.is_stock_item = 1
        doc.description = f"{self.item_name or ''} - {self.manufacturer or ''} - {self.model or ''}"
        doc.custom_clarinet_type = self.clarinet_type
        doc.custom_body_material = self.body_material
        doc.custom_keywork_plating = self.keywork_plating
        doc.custom_pitch_standard = self.pitch_standard
        doc.flags.ignore_mandatory = True
        doc.save(ignore_permissions=True)
        frappe.msgprint(_(f"Item <b>{self.item_code}</b> created/updated."))
        return doc

    def _ensure_item_prices(self, item, settings):
        self._upsert_item_price(item.item_code, self.acquisition_cost, settings.get("buying_price_list", "Standard Buying"))
        self._upsert_item_price(item.item_code, self.store_asking_price, settings.get("selling_price_list", "Standard Selling"))

    def _upsert_item_price(self, item_code, price, price_list):
        exists = frappe.db.exists("Item Price", {"item_code": item_code, "price_list": price_list})
        if exists:
            doc = frappe.get_doc("Item Price", exists)
            doc.price_list_rate = price
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item_code,
                "price_list": price_list,
                "price_list_rate": price
            })
            doc.insert(ignore_permissions=True)

    def _ensure_instrument_inspection(self, settings):
        if not self.instrument_unique_id:
            return
        inspection_type = "Initial Inspection" if self.intake_type == "New Inventory" else "Arrival Inspection"
        if self.intake_type == "New Inventory":
            inspection_type = settings.get("inspection_type_inventory", "Initial Inspection")
        else:
            inspection_type = settings.get("inspection_type_repair", "Arrival Inspection")
        existing = frappe.db.exists(
            "Instrument Inspection",
            {
                "intake_record_id": self.name,
                "instrument": self.instrument_unique_id,
            },
        )
        if existing:
            return
        inspection = frappe.get_doc({
            "doctype": "Instrument Inspection",
            "instrument": self.instrument_unique_id,
            "serial_no": self.serial_no,
            "intake_record_id": self.name,
            "inspection_type": inspection_type,
            "status": "Open"
        })
        inspection.insert(ignore_permissions=True)
        frappe.msgprint(_(f"Instrument Inspection <b>{inspection.name}</b> created and linked."))

    def _ensure_clarinet_initial_setup(self):
        existing = frappe.db.exists(
            "Clarinet Initial Setup",
            {
                "instrument": self.instrument_unique_id,
                "intake_record_id": self.name,
            },
        )
        if existing:
            return
        setup = frappe.get_doc({
            "doctype": "Clarinet Initial Setup",
            "instrument": self.instrument_unique_id,
            "serial_no": self.serial_no,
            "intake_record_id": self.name,
            "status": "Open"
        })
        setup.insert(ignore_permissions=True)
        frappe.msgprint(_(f"Clarinet Initial Setup <b>{setup.name}</b> created and linked."))

    def _validate_stock_in_inspection_warehouse(self, settings):
        warehouse = settings.get("default_inspection_warehouse") or "Clarinet Inspection"
        sn = frappe.db.exists("Serial No", {"serial_no": self.serial_no, "warehouse": warehouse})
        if not sn:
            frappe.msgprint(_(f"Warning: Serial No {self.serial_no} not found in warehouse '{warehouse}'."))
        bin_qty = frappe.db.get_value("Bin", {"item_code": self.item_code, "warehouse": warehouse}, "actual_qty")
        if not bin_qty or float(bin_qty) <= 0:
            frappe.msgprint(_(f"Warning: No stock found for Item {self.item_code} in warehouse '{warehouse}'."))

    def _generate_record_id(self) -> str:
        settings = get_intake_settings()
        pattern = settings.get("intake_naming_series") or "INV-#####"
        return naming.make_autoname(pattern)

    def _enforce_dynamic_mandatory_fields(self) -> None:
        missing = [
            self.meta.get_label(field)
            for field in MANDATORY_BY_TYPE.get(self.intake_type, set())
            if not self.get(field)
        ]
        if missing:
            message = (
                _("Missing required information:<br><ul>")
                + "".join(f"<li>{f}</li>" for f in missing)
                + "</ul>"
            )
            frappe.throw(message, title=_("Incomplete Intake"))

    def _sync_instrument_from_serial(self) -> None:
        if not self.serial_no:
            return
        instrument = frappe.db.get_value(
            "Instrument",
            {"serial_no": self.serial_no},
            ["name", "manufacturer", "model", "clarinet_type", "year_of_manufacture"],
            as_dict=True,
        )
        if instrument:
            if not self.instrument_unique_id:
                self.instrument_unique_id = instrument.get("name")
            field_map = {
                "manufacturer": "manufacturer",
                "model": "model",
                "clarinet_type": "clarinet_type",
                "year_of_manufacture": "year_of_manufacture",
            }
            for intake_field, instrument_key in field_map.items():
                if not self.get(intake_field):
                    self.set(intake_field, instrument.get(instrument_key))
        else:
            # Auto-create Instrument if not found
            instrument_doc = frappe.new_doc("Instrument")
            instrument_doc.serial_no = self.serial_no
            instrument_doc.instrument_type = self.clarinet_type or ""
            instrument_doc.brand = self.manufacturer or ""
            instrument_doc.model = self.model or ""
            instrument_doc.year_of_manufacture = self.year_of_manufacture or ""
            instrument_doc.insert(ignore_permissions=True)
            self.instrument_unique_id = instrument_doc.name
            frappe.msgprint(_(f"Instrument <b>{instrument_doc.serial_no}</b> was auto-created and linked to Intake."))

@frappe.whitelist()
def get_instrument_by_serial(serial_no: str) -> dict[str, str | int | None] | None:
    if not serial_no:
        return None
    return frappe.db.get_value(
        "Instrument",
        {"serial_no": serial_no},
        [
            "name",
            "manufacturer",
            "model",
            "clarinet_type",
            "body_material",
            "keywork_plating",
            "pitch_standard",
            "year_of_manufacture",
        ],
        as_dict=True,
    )
