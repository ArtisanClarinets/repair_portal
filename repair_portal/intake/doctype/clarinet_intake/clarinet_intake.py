# ---
# File Header:
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-21
# Version: v7.0 (Enterprise-Grade: Atomic Transactions & Advanced Logging)
# Purpose: Fortune-500 level controller for Clarinet Intake. This version ensures
#          transactional integrity for all database operations on submit.
#          Key Features:
#          1. On Save: Atomically creates a draft Instrument Inspection.
#          2. On Submit: Submits the inspection and, for "New Inventory", runs a
#             fully transactional process to create all related ERPNext documents.
#             If any step fails, the entire submission is rolled back.
# ---

from __future__ import annotations

from typing import Literal

import frappe
from frappe import _
from frappe.model import naming
from frappe.model.document import Document
from frappe.utils import nowdate

from repair_portal.intake.doctype.clarinet_intake_settings.clarinet_intake_settings import (
    get_intake_settings,
)

# Defines mandatory fields, crucial for data integrity.
MANDATORY_BY_TYPE = {
    "New Inventory": {"item_code", "item_name", "acquisition_cost", "store_asking_price"},
    "Repair": {"customer", "customers_stated_issue"},
    "Maintenance": {"customer", "customers_stated_issue"},
}

 
class ClarinetIntake(Document):
    """
    Enterprise-grade controller for the Clarinet Intake document.
    Manages data validation, state transitions, and automated document creation
    with a focus on transactional integrity and robust error handling.
    """

    # --- Type Hinting for Document Fields ---
    name: str
    intake_record_id: str
    instrument: str | None
    customer: str | None
    intake_type: Literal["New Inventory", "Repair", "Maintenance"]
    # ... (other fields)

    # --- Standard Frappe Hooks: The Entry Points of Business Logic ---
    def after_insert(self):
        self.create_instrument_inspection()

    def autoname(self) -> None:
        """Sets the document name using a settings-driven naming series."""
        if not self.intake_record_id:
            settings = get_intake_settings()
            pattern = settings.get("intake_naming_series") or "INTAKE-.{YYYY}.-.#####"
            self.intake_record_id = naming.make_autoname(pattern, doc=self)
        self.name = self.intake_record_id

    def validate(self) -> None:
        """
        Executes before `save`. This hook is for validation and pre-save data manipulation.
        """
        self._enforce_dynamic_mandatory_fields()
        self._sync_info_from_existing_instrument()
        self._ensure_inspection_on_save()

    def on_submit(self) -> None:
        """
        Executes on `submit`. Orchestrates the entire downstream process as a single
        atomic transaction. If any part of this method fails, all database changes
        are automatically rolled back by Frappe's transaction management.
        """
        try:
            settings = get_intake_settings()
            self._submit_instrument_inspection()

            if self.intake_type == "New Inventory":
                self._process_new_inventory_submission(settings)

            frappe.msgprint(
                _("Intake {0} processed successfully.").format(self.name),
                title=_("Success"),
                indicator="green",
            )
        except Exception as e:
            # Log the full error for system administrators and provide a clean message to the user.
            frappe.log_error(
                message=frappe.get_traceback(), title=_("Intake Submission Failed for {0}").format(self.name)
            )
            frappe.throw(
                _("Could not fully process the intake. Please contact support. Error: {0}").format(e)
            )

    def on_cancel(self) -> None:
        """
        Executes on `cancel`. Handles the rollback of related documents.
        """
        # This is an example of good practice. If you cancel an intake, you should
        # also cancel the linked inspection.
        try:
            inspection_name = frappe.db.get_value(
                "Instrument Inspection", {"intake_record_id": self.name, "docstatus": 1}
            )
            if inspection_name:
                inspection_doc = frappe.get_doc("Instrument Inspection", inspection_name)
                inspection_doc.cancel()
                frappe.msgprint(
                    _("Linked Instrument Inspection <b>{0}</b> cancelled.").format(inspection_name)
                )
        except Exception:
            frappe.log_error(
                frappe.get_traceback(), _("Failed to cancel linked documents for {0}").format(self.name)
            )

    # --- Orchestration Methods ---

    def _process_new_inventory_submission(self, settings: Document) -> None:
        """
        Manages the complete, ordered workflow for a "New Inventory" intake.
        This function's clarity is key for long-term maintenance.
        """
        # 1. Ensure the master 'Instrument' record exists.
        instrument = self._ensure_instrument()
        self.db_set("instrument", instrument.name)

        # 2. Ensure the corresponding ERPNext 'Item' exists.
        item = self._ensure_erpnext_item(settings, instrument)

        # 3. Register the 'Serial No' in stock. This is a critical step for inventory management.
        self._ensure_serial_no(item, settings)

        # 4. Set the item's valuation and selling prices.
        self._ensure_item_prices(item, settings)

        # 5. Create the 'Initial Setup' record if configured to do so.
        if settings.get("auto_create_initial_setup", 1):
            self._ensure_clarinet_initial_setup(instrument)
            
        # 6. Create the instrument Inspection record if configured to do so.
        if settings.get("_ensure_inspection_on_save", 1):
            self._ensure_inspection_on_save()

    # --- Helper Methods: Each performs a single, well-defined task ---

    def create_instrument_inspection(self):
        # Check if inspection already exists to avoid duplication
        existing = frappe.get_all(
            "Instrument Inspection",
            filters={"clarinet_intake": self.name},
            limit=1
        )

        if existing:
            frappe.logger("instrument_auto_log").info(
                f"Instrument Inspection already exists for Clarinet Intake {self.name}"
            )
            return

        # Create new Instrument Inspection
        inspection = frappe.new_doc("Instrument Inspection")
        inspection.clarinet_intake = self.name

        # Copy over relevant fields, adjust these as per your model
        inspection.customer = self.customer if hasattr(self, "customer") else None
        inspection.instrument_type = "Clarinet"
        inspection.status = "Pending"

        # Insert and commit
        inspection.insert(ignore_permissions=True)

        # Optional: feedback for user (in UI)
        frappe.msgprint(f"Created Instrument Inspection: {inspection.name}")

        

        if existing:
            frappe.logger("instrument_auto_log").info(
                f"Instrument Inspection already exists for Clarinet Intake {self.name}"
            )
            return

        # Create new Instrument Inspection
        inspection = frappe.new_doc("Instrument Inspection")
        inspection.clarinet_intake = self.name

        # Copy over relevant fields, adjust these as per your model
        inspection.customer = self.customer if hasattr(self, "customer") else None
        inspection.instrument_type = "Clarinet"
        inspection.status = "Pending"

        # Insert and commit
        inspection.insert(ignore_permissions=True)

        # Optional: feedback for user (in UI)
        frappe.msgprint(f"Created Instrument Inspection: {inspection.name}")
    def _ensure_inspection_on_save(self) -> None:
        """
        Atomically creates a DRAFT Instrument Inspection on the first save.
        Called from `validate` to ensure it's part of the save transaction.
        """
        if self.is_new():  # Only run on the very first save.
            try:
                settings = get_intake_settings()
                inspection_type = (
                    settings.get("inspection_type_inventory", "Initial Inspection")
                    if self.intake_type == "New Inventory"
                    else settings.get("inspection_type_repair", "Repair")
                )
                inspection = frappe.new_doc("Instrument Inspection")
                inspection.intake_record_id = self.name
                inspection.customer = self.customer
                inspection.inspection_date = self.date or nowdate()
                inspection.inspection_type = inspection_type
                inspection.insert(ignore_permissions=True)  # Will be in Draft status (docstatus=0)
                frappe.msgprint(_("Draft Instrument Inspection <b>{0}</b> created.").format(inspection.name))
            except Exception as e:
                # If this fails, the entire save operation should be aborted.
                frappe.throw(_("Failed to create draft inspection: {0}").format(e))

    def _submit_instrument_inspection(self) -> None:
        """Finds the linked draft inspection and submits it."""
        inspection_name = frappe.db.get_value(
            "Instrument Inspection", {"intake_record_id": self.name, "docstatus": 0}
        )
        if inspection_name:
            inspection_doc = frappe.get_doc("Instrument Inspection", inspection_name)
            inspection_doc.submit()
            frappe.msgprint(_("Instrument Inspection <b>{0}</b> submitted.").format(inspection_doc.name))

    def _ensure_instrument(self) -> Document:
        """
        Gets an existing Instrument by its unique serial number, or creates a new one.
        Returns the Instrument document.
        """
        if not self.serial_no:
            frappe.throw(_("Serial Number is required to create or identify an Instrument."))

        instrument_doc = frappe.db.exists("Instrument", {"serial_no": self.serial_no})
        if instrument_doc:
            return frappe.get_doc("Instrument", instrument_doc)

        new_instrument = frappe.new_doc("Instrument")
        new_instrument.serial_no = self.serial_no
        new_instrument.brand = self.manufacturer
        new_instrument.model = self.model
        new_instrument.instrument_type = self.clarinet_type
        new_instrument.insert(ignore_permissions=True)
        return new_instrument

    def _ensure_erpnext_item(self, settings: Document, instrument: Document) -> Document:
        """
        Creates or updates an Item in ERPNext, ensuring it's linked to the Instrument.
        Returns the Item document.
        """
        item_doc = frappe.db.exists("Item", {"item_code": self.item_code})
        doc = frappe.get_doc("Item", item_doc) if item_doc else frappe.new_doc("Item")

        doc.item_code = self.item_code
        doc.item_name = self.item_name
        doc.item_group = settings.get("default_item_group") or "Products"
        doc.brand = instrument.brand
        doc.stock_uom = settings.get("stock_uom") or "Nos"
        doc.is_stock_item = 1
        doc.has_serial_no = 1
        doc.custom_instrument = instrument.name  # Assumes 'custom_instrument' link field exists on Item
        doc.save(ignore_permissions=True)
        return doc

    def _ensure_serial_no(self, item: Document, settings: Document) -> None:
        """Creates the ERPNext Serial No document to register the item in stock."""
        warehouse = settings.get("default_inspection_warehouse")
        if not warehouse:
            frappe.throw(_("Default Inspection Warehouse is not set in Clarinet Intake Settings."))

        if not frappe.db.exists("Serial No", {"serial_no": self.serial_no}):
            frappe.get_doc(
                {
                    "doctype": "Serial No",
                    "serial_no": self.serial_no,
                    "item_code": item.item_code,
                    "warehouse": warehouse,
                }
            ).insert(ignore_permissions=True)

    def _ensure_item_prices(self, item: Document, settings: Document) -> None:
        """Creates or updates the buying and selling prices for the item."""
        if settings.get("buying_price_list"):
            self._upsert_item_price(item.item_code, self.acquisition_cost, settings.get("buying_price_list"))
        if settings.get("selling_price_list"):
            self._upsert_item_price(
                item.item_code, self.store_asking_price, settings.get("selling_price_list")
            )

    def _upsert_item_price(self, item_code: str, price: float, price_list: str) -> None:
        """Utility to create or update an Item Price record idempotently."""
        price_doc_name = frappe.db.exists("Item Price", {"item_code": item_code, "price_list": price_list})
        price_doc = (
            frappe.get_doc("Item Price", price_doc_name) if price_doc_name else frappe.new_doc("Item Price")
        )
        price_doc.item_code = item_code
        price_doc.price_list = price_list
        price_doc.price_list_rate = price
        price_doc.save(ignore_permissions=True)

    def _ensure_clarinet_initial_setup(self, instrument: Document) -> None:
        """Creates the Clarinet Initial Setup record."""
        if not frappe.db.exists("Clarinet Initial Setup", {"instrument": instrument.name}):
            setup = frappe.new_doc("Clarinet Initial Setup")
            setup.instrument = instrument.name
            setup.date = self.date or nowdate()
            setup.insert(ignore_permissions=True).submit()

    def _enforce_dynamic_mandatory_fields(self) -> None:
        """Validates that all required fields for the intake type are filled."""
        missing = [
            self.meta.get_label(f) for f in MANDATORY_BY_TYPE.get(self.intake_type, set()) if not self.get(f)
        ]
        if missing:
            frappe.throw(
                _("Required fields are missing: {0}").format(", ".join(missing)), title=_("Validation Error")
            )

    def _sync_info_from_existing_instrument(self) -> None:
        """On validation, if a serial number is provided, fetches and syncs data."""
        if self.serial_no and not self.instrument:
            instrument = frappe.db.get_value(
                "Instrument", {"serial_no": self.serial_no}, ["name", "brand", "model"], as_dict=True
            )
            if instrument:
                self.instrument = instrument.name
                if not self.manufacturer:
                    self.manufacturer = instrument.brand
                if not self.model:
                    self.model = instrument.model


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
