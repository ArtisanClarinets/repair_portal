# Copyright (c) 2024, jHetzer and contributors
# For license information, please see license.txt

# ---
# File Header:
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-21
# Version: v5.1 (Refactor: Brand Mapping Table)
# Purpose: Controller logic for Clarinet Intake. On submit, this controller now:
#          1. ALWAYS creates an Instrument Inspection.
#          2. For "New Inventory" type: Creates/updates Instrument, ERPNext Item, ERPNext Serial No, and Initial Setup.
#          Logic is settings-driven via 'Clarinet Intake Settings'.
# ---

from __future__ import annotations
import frappe
from frappe import _
from frappe.model import naming
from frappe.model.document import Document
from repair_portal.intake.doctype.clarinet_intake_settings.clarinet_intake_settings import get_intake_settings
from typing import Literal

# Defines which fields are mandatory based on the intake type.
MANDATORY_BY_TYPE = {
    "New Inventory": {
        "body_material",
        "acquisition_source",
        "acquisition_cost",
        "store_asking_price",
        "item_code",
        "item_name",
    },
    "Repair": {"customers_stated_issue", "service_type_requested", "customer"},
    "Maintenance": {"customers_stated_issue", "service_type_requested", "customer"},
}


def get_brand_map(settings) -> dict:
    """
    Returns a dict {from_brand: to_brand} using the table, not JSON.
    """
    rules = settings.get("brand_mapping_rules", [])
    if not rules:
        return {}
    # If child table rows are dicts
    return {row.get("from_brand"): row.get("to_brand") for row in rules if row.get("from_brand") and row.get("to_brand")}


class ClarinetIntake(Document):
    """Business logic & validation for the Clarinet Intake document."""

    # --- Type Hinting for Document Fields ---
    name: str
    intake_record_id: str
    instrument: str | None
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
    consent_liability_waiver: str | None
    inspection_type: str | None

    def autoname(self) -> None:
        settings = get_intake_settings()
        if not self.intake_record_id:
            pattern = settings.get("intake_naming_series") or "INTAKE-.#####"
            self.intake_record_id = naming.make_autoname(pattern)
        self.name = self.intake_record_id

    def validate(self) -> None:
        self._enforce_dynamic_mandatory_fields()
        self._sync_info_from_existing_instrument()

    def on_submit(self) -> None:
        settings = get_intake_settings()
        # --- STEP 1: Always create Instrument Inspection ---
        self._ensure_instrument_inspection(settings)
        # --- STEP 2: For New Inventory, do orchestration ---
        if self.intake_type == "New Inventory":
            try:
                instrument = self._ensure_instrument(settings)
                self.db_set("instrument", instrument.name)
                item = self._ensure_erpnext_item(settings, instrument)
                self._ensure_serial_no(item, settings)
                self._ensure_item_prices(item, settings)
                if settings.get("auto_create_initial_setup", 1):
                    self._ensure_clarinet_initial_setup(instrument)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), _("New Inventory Processing Failed"))
                frappe.throw(_("Failed to process New Inventory intake: {0}").format(e))
        frappe.msgprint(_("Intake {0} submitted successfully.").format(self.name), alert=True, indicator="green")

    # --- Validation helpers ---
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

    def _sync_info_from_existing_instrument(self) -> None:
        if not self.serial_no:
            return
        instrument = frappe.db.get_value(
            "Instrument",
            {"serial_no": self.serial_no},
            ["name", "brand", "model", "clarinet_type"],
            as_dict=True,
        )
        if instrument:
            self.instrument = instrument.get("name")
            if not self.manufacturer:
                self.manufacturer = instrument.get("brand")
            if not self.model:
                self.model = instrument.get("model")
            if not self.clarinet_type:
                self.clarinet_type = instrument.get("clarinet_type")

    # --- Document creation helpers ---
    def _ensure_instrument(self, settings=None) -> Document:
        # settings param is for future mapping/logic needs
        # Map brand using brand_mapping_rules
        mapped_manufacturer = self.manufacturer
        if settings:
            brand_map = get_brand_map(settings)
            if self.manufacturer in brand_map:
                mapped_manufacturer = brand_map[self.manufacturer]
        if frappe.db.exists("Instrument", {"serial_no": self.serial_no}):
            instrument_doc = frappe.get_doc("Instrument", {"serial_no": self.serial_no})
        else:
            instrument_doc = frappe.new_doc("Instrument")
            instrument_doc.serial_no = self.serial_no
            instrument_doc.brand = mapped_manufacturer
            instrument_doc.model = self.model
            instrument_doc.instrument_type = self.clarinet_type
            instrument_doc.insert(ignore_permissions=True)
            frappe.msgprint(_("New Instrument <b>{0}</b> created.").format(instrument_doc.name))
        return instrument_doc

    def _ensure_erpnext_item(self, settings: Document, instrument: Document) -> Document:
        if frappe.db.exists("Item", {"item_code": self.item_code}):
            item_doc = frappe.get_doc("Item", self.item_code)
        else:
            item_doc = frappe.new_doc("Item")
        item_doc.item_code = self.item_code
        item_doc.item_name = self.item_name
        item_doc.item_group = settings.get("default_item_group") or "Products"
        item_doc.brand = instrument.brand
        item_doc.stock_uom = settings.get("stock_uom") or "Nos"
        item_doc.is_stock_item = 1
        item_doc.has_serial_no = 1
        item_doc.custom_instrument = instrument.name
        item_doc.save(ignore_permissions=True)
        frappe.msgprint(_("ERPNext Item <b>{0}</b> created/updated.").format(self.item_code))
        return item_doc

    def _ensure_serial_no(self, item: Document, settings: Document) -> None:
        warehouse = settings.get("default_inspection_warehouse")
        if not warehouse:
            frappe.throw(_("Please set the 'Default Inspection Warehouse' in Clarinet Intake Settings."))
        if not frappe.db.exists("Serial No", {"serial_no": self.serial_no, "item_code": item.item_code}):
            serial_no_doc = frappe.new_doc("Serial No")
            serial_no_doc.serial_no = self.serial_no
            serial_no_doc.item_code = item.item_code
            serial_no_doc.warehouse = warehouse
            serial_no_doc.insert(ignore_permissions=True)
            frappe.msgprint(
                _("Serial Number <b>{0}</b> registered in warehouse '{1}'.").format(self.serial_no, warehouse)
            )

    def _ensure_item_prices(self, item: Document, settings: Document) -> None:
        if settings.get("buying_price_list"):
            self._upsert_item_price(item.item_code, self.acquisition_cost, settings.get("buying_price_list"))
        if settings.get("selling_price_list"):
            self._upsert_item_price(
                item.item_code, self.store_asking_price, settings.get("selling_price_list")
            )

    def _upsert_item_price(self, item_code: str, price: float, price_list: str) -> None:
        price_doc_name = frappe.db.exists("Item Price", {"item_code": item_code, "price_list": price_list})
        if price_doc_name:
            price_doc = frappe.get_doc("Item Price", price_doc_name)
        else:
            price_doc = frappe.new_doc("Item Price")
            price_doc.item_code = item_code
            price_doc.price_list = price_list
        price_doc.price_list_rate = price
        price_doc.save(ignore_permissions=True)

    def _ensure_instrument_inspection(self, settings: Document) -> None:
        if frappe.db.exists("Instrument Inspection", {"intake_record_id": self.name}):
            return
        inspection = frappe.new_doc("Instrument Inspection")
        inspection.intake_record_id = self.name
        inspection.customer = self.customer
        inspection.inspection_date = self.date
        inspection.status = "Open"
        if self.intake_type == "New Inventory":
            inspection.inspection_type = settings.get("inspection_type_inventory", "Initial Inspection")
        else:
            inspection.inspection_type = settings.get("inspection_type_repair", "Arrival Inspection")
        inspection.insert(ignore_permissions=True)
        inspection.submit()
        frappe.msgprint(_("Instrument Inspection <b>{0}</b> created.").format(inspection.name))

    def _ensure_clarinet_initial_setup(self, instrument: Document) -> None:
        if frappe.db.exists("Clarinet Initial Setup", {"instrument": instrument.name}):
            return
        setup = frappe.new_doc("Clarinet Initial Setup")
        setup.instrument = instrument.name
        setup.date = self.date
        setup.status = "Open"
        setup.insert(ignore_permissions=True)
        setup.submit()
        frappe.msgprint(_("Clarinet Initial Setup <b>{0}</b> created.").format(setup.name))

@frappe.whitelist()
def get_instrument_by_serial(serial_no: str) -> dict[str, str | int | None] | None:
    if not serial_no:
        return None
    data = frappe.db.get_value(
        "Instrument",
        {"serial_no": serial_no},
        [
            "name",
            "brand",
            "model",
            "clarinet_type",
            "body_material",
            "key_plating",
            "year_of_manufacture",
        ],
        as_dict=True,
    )
    if data:
        data["manufacturer"] = data.pop("brand", None)
    return data
