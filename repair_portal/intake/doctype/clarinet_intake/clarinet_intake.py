# File Header Template
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-19
# Version: v3.5
# Purpose: Controller logic for Clarinet Intake. Handles validation, naming,
# triggers inventory/repair automation, Item/Price/Warehouse/Brand/supplier_code mapping, and always creates Instrument Inspection and Initial Setup.
# Dependencies: ERPNext Item, Item Price, Serial No, Instrument, Instrument Inspection, Clarinet Initial Setup

from __future__ import annotations

from typing import Literal

import frappe
from frappe import _
from frappe.model import naming
from frappe.model.document import Document

MANDATORY_BY_TYPE = {
    "New Inventory": {"body_material", "acquisition_source", "acquisition_cost", "store_asking_price", "item_code", "item_name"},
    "Repair": {"customers_stated_issue", "service_type_requested", "customer"},
    "Maintenance": {"customers_stated_issue", "service_type_requested", "customer"},
}

CLARINET_INSPECTION_WAREHOUSE = "Clarinet Inspection"  # Set this to your actual warehouse name

class ClarinetIntake(Document):
    """Business logic & validation for the Clarinet Intake document."""
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
        if not self.intake_record_id:
            self.intake_record_id = self._generate_record_id()
        self.name = self.intake_record_id

    def validate(self) -> None:
        self._enforce_dynamic_mandatory_fields()
        self._sync_instrument_from_serial()

    def on_submit(self) -> None:
        if self.intake_type == "New Inventory":
            try:
                item = self._ensure_erpnext_item()
                self._ensure_item_prices(item)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), _("Item creation/price failed"))
                frappe.throw(_(f"Failed to create Item/Prices: {e}"))
        try:
            self._ensure_instrument_inspection()
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Instrument Inspection creation failed"))
            frappe.throw(_(f"Failed to create Instrument Inspection: {e}"))
        # Always try to create initial setup for inventory
        if self.intake_type == "New Inventory":
            try:
                self._ensure_clarinet_initial_setup()
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), _("Clarinet Initial Setup failed"))
                frappe.msgprint(_(f"Warning: Initial Setup could not be created: {e}"))
        # Stock validation & notification
        try:
            self._validate_stock_in_inspection_warehouse()
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Stock Validation failed"))
            frappe.msgprint(_(f"Warning: Stock validation error: {e}"))

    def _ensure_erpnext_item(self):
        """Create or update Item with mapping for group, brand, warehouse, supplier code."""
        item = frappe.db.exists("Item", {"item_code": self.item_code})
        doc = frappe.get_doc("Item", item) if item else frappe.new_doc("Item")
        doc.item_code = self.item_code
        doc.item_name = self.item_name
        doc.item_group = "Clarinets"
        doc.brand = self.manufacturer or "Unknown"
        doc.default_warehouse = CLARINET_INSPECTION_WAREHOUSE
        doc.supplier_code = self.item_code  # assumes custom field
        doc.stock_uom = "Nos"
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

    def _ensure_item_prices(self, item):
        """Create or update Item Prices for buying/selling."""
        self._upsert_item_price(item.item_code, self.acquisition_cost, "Standard Buying")
        self._upsert_item_price(item.item_code, self.store_asking_price, "Standard Selling")

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

    def _ensure_instrument_inspection(self) -> None:
        if not self.instrument_unique_id:
            return
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
            "inspection_type": "Initial Inspection" if self.intake_type == "New Inventory" else "Arrival Inspection",
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

    def _validate_stock_in_inspection_warehouse(self):
        """Notify if Item/Serial not present in inspection warehouse."""
        sn = frappe.db.exists("Serial No", {"serial_no": self.serial_no, "warehouse": CLARINET_INSPECTION_WAREHOUSE})
        if not sn:
            frappe.msgprint(_(f"Warning: Serial No {self.serial_no} not found in warehouse '{CLARINET_INSPECTION_WAREHOUSE}'."))
        bin_qty = frappe.db.get_value("Bin", {"item_code": self.item_code, "warehouse": CLARINET_INSPECTION_WAREHOUSE}, "actual_qty")
        if not bin_qty or float(bin_qty) <= 0:
            frappe.msgprint(_(f"Warning: No stock found for Item {self.item_code} in warehouse '{CLARINET_INSPECTION_WAREHOUSE}'."))

    def _generate_record_id(self) -> str:
        prefix_map = {"New Inventory": "INV", "Repair": "REP", "Maintenance": "MAIN"}
        prefix = prefix_map.get(self.intake_type, "INT")
        return f"{prefix}-{naming.make_autoname('#####')}"

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
