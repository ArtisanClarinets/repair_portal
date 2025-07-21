# Copyright (c) 2024, jHetzer and contributors
# For license information, please see license.txt

# ---
# File Header:
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-21
# Version: v5.0 (Refactored for on_submit orchestration)
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
import json
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


class ClarinetIntake(Document):
    """Business logic & validation for the Clarinet Intake document."""

    # --- Type Hinting for Document Fields ---
    name: str
    intake_record_id: str
    instrument: str | None  # Changed from instrument_unique_id for clarity
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

    # --- Standard Frappe Hooks ---

    def autoname(self) -> None:
        """Sets the document name based on a naming series from settings."""
        settings = get_intake_settings()
        if not self.intake_record_id:
            pattern = settings.get("intake_naming_series") or "INTAKE-.#####"
            self.intake_record_id = naming.make_autoname(pattern)
        self.name = self.intake_record_id

    def validate(self) -> None:
        """Runs before 'save'. Used for data validation and pre-save logic."""
        self._enforce_dynamic_mandatory_fields()
        self._sync_info_from_existing_instrument()

    def on_submit(self) -> None:
        """
        Runs after 'submit'. This is the main orchestrator for creating other documents.
        """
        settings = get_intake_settings()

        # STEP 1: Always create the Instrument Inspection for every intake type.
        # This logic is now unconditional to meet the requirement.
        self._ensure_instrument_inspection(settings)

        # STEP 2: For "New Inventory" intakes, create all related ERPNext documents.
        if self.intake_type == "New Inventory":
            try:
                # Create or update the core Instrument document first.
                instrument = self._ensure_instrument()

                # Link the newly created/verified instrument back to this intake.
                self.db_set("instrument", instrument.name)

                # Create the corresponding ERPNext Item, linked to the Instrument.
                item = self._ensure_erpnext_item(settings, instrument)

                # Create the ERPNext Serial No, which makes the item available in stock.
                self._ensure_serial_no(item, settings)

                # Set the buying and selling prices for the item.
                self._ensure_item_prices(item, settings)

                # Finally, create the initial setup record if enabled in settings.
                if settings.get("auto_create_initial_setup", 1):
                    self._ensure_clarinet_initial_setup(instrument)

            except Exception as e:
                frappe.log_error(frappe.get_traceback(), _("New Inventory Processing Failed"))
                frappe.throw(_("Failed to process New Inventory intake: {0}").format(e))

        frappe.msgprint(
            _("Intake {0} submitted successfully.").format(self.name), alert=True, indicator="green"
        )

    # --- Helper Methods for Validation ---

    def _enforce_dynamic_mandatory_fields(self) -> None:
        """Checks if all required fields for the selected intake_type are filled."""
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
        """
        During validation, if a serial number is entered, this fetches data
        from an existing Instrument to auto-fill fields.
        It does NOT create an instrument; creation now happens `on_submit`.
        """
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
            # Map Instrument fields to Intake fields if they are empty
            if not self.manufacturer:
                self.manufacturer = instrument.get("brand")
            if not self.model:
                self.model = instrument.get("model")
            if not self.clarinet_type:
                self.clarinet_type = instrument.get("clarinet_type")

    # --- Helper Methods for Document Creation (`on_submit`) ---

    def _ensure_instrument(self) -> Document:
        """
        Finds an existing Instrument by serial number or creates a new one.
        This is the single source of truth for instrument creation.
        Returns the Instrument document.
        """
        if frappe.db.exists("Instrument", {"serial_no": self.serial_no}):
            instrument_doc = frappe.get_doc("Instrument", {"serial_no": self.serial_no})
        else:
            instrument_doc = frappe.new_doc("Instrument")
            instrument_doc.serial_no = self.serial_no
            instrument_doc.brand = self.manufacturer  # Maps Intake 'manufacturer' to Instrument 'brand'
            instrument_doc.model = self.model
            instrument_doc.instrument_type = self.clarinet_type
            instrument_doc.insert(ignore_permissions=True)
            frappe.msgprint(_("New Instrument <b>{0}</b> created.").format(instrument_doc.name))

        return instrument_doc

    def _ensure_erpnext_item(self, settings: Document, instrument: Document) -> Document:
        """
        Creates or updates an Item in ERPNext.
        Now links the item directly to the Instrument document.
        """
        if frappe.db.exists("Item", {"item_code": self.item_code}):
            item_doc = frappe.get_doc("Item", self.item_code)
        else:
            item_doc = frappe.new_doc("Item")

        item_doc.item_code = self.item_code
        item_doc.item_name = self.item_name
        item_doc.item_group = settings.get("default_item_group") or "Products"
        item_doc.brand = instrument.brand  # Use brand from the instrument document
        item_doc.stock_uom = settings.get("stock_uom") or "Nos"
        item_doc.is_stock_item = 1
        item_doc.has_serial_no = 1  # Crucial for serialized inventory

        # Link to the instrument
        item_doc.custom_instrument = (
            instrument.name
        )  # Assuming you have a custom field 'custom_instrument' of type Link on your Item doctype

        item_doc.save(ignore_permissions=True)
        frappe.msgprint(_("ERPNext Item <b>{0}</b> created/updated.").format(self.item_code))
        return item_doc

    def _ensure_serial_no(self, item: Document, settings: Document) -> None:
        """Creates the ERPNext Serial No document, making the item available in stock."""
        warehouse = settings.get("default_inspection_warehouse")
        if not warehouse:
            frappe.throw(_("Please set the 'Default Inspection Warehouse' in Clarinet Intake Settings."))

        if not frappe.db.exists("Serial No", {"serial_no": self.serial_no, "item_code": item.item_code}):
            serial_no_doc = frappe.new_doc("Serial No")
            serial_no_doc.serial_no = self.serial_no
            serial_no_doc.item_code = item.item_code
            serial_no_doc.warehouse = warehouse  # Set the warehouse from settings
            serial_no_doc.insert(ignore_permissions=True)
            frappe.msgprint(
                _("Serial Number <b>{0}</b> registered in warehouse '{1}'.").format(self.serial_no, warehouse)
            )

    def _ensure_item_prices(self, item: Document, settings: Document) -> None:
        """Creates or updates the buying and selling prices for the item."""
        if settings.get("buying_price_list"):
            self._upsert_item_price(item.item_code, self.acquisition_cost, settings.get("buying_price_list"))
        if settings.get("selling_price_list"):
            self._upsert_item_price(
                item.item_code, self.store_asking_price, settings.get("selling_price_list")
            )

    def _upsert_item_price(self, item_code: str, price: float, price_list: str) -> None:
        """Utility to create or update an Item Price record."""
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
        """Creates the Instrument Inspection record, now linked to the intake."""
        # This check prevents creating a duplicate inspection if the doc is amended and re-submitted.
        if frappe.db.exists("Instrument Inspection", {"intake_record_id": self.name}):
            return

        inspection = frappe.new_doc("Instrument Inspection")
        inspection.intake_record_id = self.name  # Link back to this intake
        inspection.customer = self.customer
        inspection.inspection_date = self.date
        inspection.status = "Open"

        # Determine inspection type from settings
        if self.intake_type == "New Inventory":
            inspection.inspection_type = settings.get("inspection_type_inventory", "Initial Inspection")
        else:
            inspection.inspection_type = settings.get("inspection_type_repair", "Arrival Inspection")

        inspection.insert(ignore_permissions=True)
        inspection.submit()
        frappe.msgprint(_("Instrument Inspection <b>{0}</b> created.").format(inspection.name))

    def _ensure_clarinet_initial_setup(self, instrument: Document) -> None:
        """Creates the Clarinet Initial Setup record, linked to the new Instrument."""
        if frappe.db.exists("Clarinet Initial Setup", {"instrument": instrument.name}):
            return

        setup = frappe.new_doc("Clarinet Initial Setup")
        setup.instrument = instrument.name  # Link to the instrument
        setup.date = self.date
        setup.status = "Open"
        setup.insert(ignore_permissions=True)
        setup.submit()
        frappe.msgprint(_("Clarinet Initial Setup <b>{0}</b> created.").format(setup.name))


# This whitelisted function remains unchanged. It is used for fetching data on the client-side.
@frappe.whitelist()
def get_instrument_by_serial(serial_no: str) -> dict[str, str | int | None] | None:
    """
    Fetch Instrument by serial_no, mapping Instrument.brand -> manufacturer.
    Args:
        serial_no (str): Serial number of instrument.
    Returns:
        dict or None: Instrument info (brand is mapped to manufacturer)
    """
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
        # Map Instrument.brand to manufacturer for frontend compatibility
        data["manufacturer"] = data.pop("brand", None)
    return data
