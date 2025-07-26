# ---
# File Header:
# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-22
# Version: v9.1.1 (Initial Setup intake link patch)
# Purpose: Ensures all intake types auto-create Instrument, Item, Serial No, and Instrument Inspection as needed, plus Clarinet Initial Setup for New Inventory. Handles Instrument Category and Initial Setup-intake link.
# Dependencies: Clarinet Intake Settings, Instrument, Item, Serial No, Instrument Inspection, Clarinet Initial Setup, Instrument Category

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

MANDATORY_BY_TYPE = {
    "New Inventory": {"item_code", "item_name", "acquisition_cost", "store_asking_price"},
    "Repair": {"customer", "customers_stated_issue"},
    "Maintenance": {"customer", "customers_stated_issue"},
}

class ClarinetIntake(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_profile.doctype.instrument_accessory.instrument_accessory import InstrumentAccessory

        accessory_id: DF.Table[InstrumentAccessory]
        acquisition_cost: DF.Currency
        acquisition_source: DF.Data | None
        amended_from: DF.Link | None
        body_material: DF.Data | None
        bore_type: DF.Data | None
        clarinet_type: DF.Literal["B\u266d Clarinet", "A Clarinet", "E\u266d Clarinet", "Bass Clarinet", "Alto Clarinet", "Contrabass Clarinet", "Other"]
        consent_liability_waiver: DF.Link | None
        cork_condition: DF.Literal["Excellent", "Acceptable", "Needs Attention"]
        customer: DF.Link | None
        customer_approval: DF.Data | None
        customer_email: DF.Data | None
        customer_full_name: DF.Data | None
        customer_phone: DF.Data | None
        customer_type: DF.Literal["Professional", "Student", "University", "Collector"]
        customers_stated_issue: DF.SmallText | None
        deposit_paid: DF.Currency
        employee: DF.Link | None
        estimated_cost: DF.Currency
        initial_assessment_notes: DF.SmallText | None
        initial_intake_photos: DF.Attach | None
        instrument: DF.Link | None
        instrument_category: DF.Link
        intake_date: DF.Datetime | None
        intake_record_id: DF.Data | None
        intake_status: DF.Literal["Received", "Pending", "In Progress", "Inspection", "Setup", "Repair", "Awaiting Customer Approval", "Awaiting Payment", "In Transit", "Repair Complete", "Returned to Customer"]
        intake_type: DF.Literal["New Inventory", "Repair", "Maintenance"]
        item_code: DF.Data | None
        item_name: DF.Data | None
        key_plating: DF.Data | None
        keywork_condition: DF.Literal["Excellent", "Acceptable", "Needs Attention"]
        manufacturer: DF.Link
        model: DF.Data
        pad_condition: DF.Literal["Excellent", "Acceptable", "Needs Attention"]
        pitch_standard: DF.Data | None
        promised_completion_date: DF.Date | None
        serial_no: DF.Data
        service_type_requested: DF.Literal["COA", "Overhaul", "Crack Repair", "Play Condition"]
        spring_condition: DF.Literal["Excellent", "Acceptable", "Needs Attention"]
        store_asking_price: DF.Currency
        thumb_rest_type: DF.Data | None
        tone_hole_style: DF.Data | None
        wood_body_condition: DF.Literal["Excellent", "Acceptable", "Needs Attention"]
        work_order_number: DF.Link | None
        year_of_manufacture: DF.Int
    # end: auto-generated types
    """
    Controller for the Clarinet Intake document.
    Ensures all automations for Item, Serial No, Instrument, and Inspection are handled for every intake type.
    Instrument Category is handled as Link field throughout.
    Initial Setup is now linked to Intake.
    """
    name: str
    intake_record_id: str
    instrument: str | None
    customer: str | None
    intake_type: Literal["New Inventory", "Repair", "Maintenance"]

    def after_insert(self):
        settings = get_intake_settings()
        try:
            # --- 1. ITEM CREATION (ERPNext) --- #
            item_name = self.item_name or self.model or "Instrument"
            item_code = self.item_code or self.serial_no
            item = None
            if self.intake_type == "New Inventory":
                if item_code and not frappe.db.exists("Item", {"item_code": item_code}):
                    item = frappe.new_doc("Item")
                    item.item_code = item_code
                    item.item_name = item_name
                    item.item_group = settings.get("default_item_group") or "Clarinets"
                    item.stock_uom = settings.get("stock_uom") or "Nos"
                    item.description = f"{self.model or ''} {self.body_material or ''} {self.key_plating or ''}".strip()
                    item.is_stock_item = 1
                    item.disabled = 0
                    item.save(ignore_permissions=True)
                else:
                    item = frappe.get_doc("Item", item_code) if item_code else None

            # --- 2. SERIAL NO CREATION (ERPNext) --- #
            serial_no = self.serial_no
            serial = None
            serial_exists = serial_no and frappe.db.exists("Serial No", {"serial_no": serial_no})
            if not serial_exists and serial_no:
                serial = frappe.new_doc("Serial No")
                serial.serial_no = serial_no
                serial.item_code = item_code or (item.item_code if item else None) or "Customer Instrument"
                serial.status = "Active"
                serial.save(ignore_permissions=True)
            elif serial_exists:
                serial = frappe.get_doc("Serial No", {"serial_no": serial_no})

            # --- 3. INSTRUMENT CREATION (Custom Doctype) --- #
            instrument = None
            if serial_no:
                inst = frappe.db.get_value("Instrument", {"serial_no": serial_no}, ["name"], as_dict=True)
                if not inst:
                    instrument = frappe.new_doc("Instrument")
                    instrument.serial_no = serial_no
                    instrument.instrument_type = self.clarinet_type or "B♭ Clarinet"
                    instrument.brand = self.manufacturer
                    instrument.model = self.model
                    instrument.body_material = self.body_material
                    instrument.keywork_plating = self.key_plating
                    instrument.pitch_standard = self.pitch_standard
                    instrument.customer = self.customer if self.intake_type != "New Inventory" else None
                    instrument.current_status = "Active"
                    # PATCH: instrument_category as Link
                    if self.instrument_category and frappe.db.exists("Instrument Category", self.instrument_category):
                        instrument.instrument_category = self.instrument_category
                    else:
                        # fallback: set to first active category if possible
                        default_cat = frappe.db.get_value("Instrument Category", {"is_active": 1}, "name")
                        if default_cat:
                            instrument.instrument_category = default_cat
                    instrument.insert(ignore_permissions=True)
                    self.instrument = instrument.name
                else:
                    self.instrument = inst["name"]

            # --- 4. Instrument Inspection (all types) --- #
            if not frappe.db.exists("Instrument Inspection", {"intake_record_id": self.name}):
                inspection = frappe.new_doc("Instrument Inspection")
                inspection.intake_record_id = self.name
                inspection.customer = self.customer
                inspection.serial_no = self.serial_no
                inspection.instrument = self.instrument
                inspection.brand = self.manufacturer
                inspection.manufacturer = self.manufacturer  # Always set for validation
                inspection.model = self.model
                inspection.clarinet_type = self.clarinet_type
                inspection.body_material = self.body_material
                inspection.key_plating = self.key_plating
                inspection.inspection_date = self.intake_date or nowdate()
                inspection.status = "Pending"
                # Robust inspected_by fallback
                inspected_by_meta = frappe.get_meta("Instrument Inspection").get_field("inspected_by")
                inspected_by_options = (inspected_by_meta.options or "User") if inspected_by_meta else "User"
                inspected_by_value = None
                if self.employee and frappe.db.exists(inspected_by_options, self.employee):
                    inspected_by_value = self.employee
                if not inspected_by_value and frappe.session.user:
                    if inspected_by_options == "Employee":
                        emp = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
                        if emp:
                            inspected_by_value = emp
                    elif frappe.db.exists(inspected_by_options, frappe.session.user):
                        inspected_by_value = frappe.session.user
                if not inspected_by_value and getattr(self, 'inspected_by', None):
                    if frappe.db.exists(inspected_by_options, self.inspected_by):
                        inspected_by_value = self.inspected_by
                if not inspected_by_value:
                    frappe.throw(_(
                        f"Cannot create Instrument Inspection: No valid Employee/User found for 'inspected_by'. "
                        f"Tried employee: {self.employee or ''}, session_user: {frappe.session.user}, inspected_by: {getattr(self, 'inspected_by', None)}. "
                        f"Please ensure at least one exists as a {inspected_by_options} record."
                    ))
                inspection.inspected_by = inspected_by_value
                allowed_inspection_types = ["New Inventory", "Repair", "Maintenance", "QA", "Other"]
                inspection.inspection_type = self.intake_type if self.intake_type in allowed_inspection_types else "Other"
                inspection.insert(ignore_permissions=True)
                frappe.msgprint(_(f"Instrument Inspection <b>{inspection.name}</b> created."))

            # --- 5. Clarinet Initial Setup (new inventory only) --- #
            if (
                self.intake_type == "New Inventory"
                and settings.get("auto_create_initial_setup", 1)
                and self.instrument
                and not frappe.db.exists("Clarinet Initial Setup", {"instrument": self.instrument})
            ):
                setup = frappe.new_doc("Clarinet Initial Setup")
                setup.instrument = self.instrument
                setup.intake = self.name  # PATCH: Link Initial Setup to Intake
                setup.setup_date = self.intake_date or nowdate()
                setup.status = "Open"
                setup.insert(ignore_permissions=True)
                frappe.msgprint(_(f"Clarinet Initial Setup <b>{setup.name}</b> created."))

        except Exception:
            frappe.log_error(frappe.get_traceback(), "ClarinetIntake.after_insert")
            frappe.throw(_("An error occurred during automated record creation. Please check system logs or contact an administrator."))

    def autoname(self) -> None:
        if not self.intake_record_id:
            settings = get_intake_settings()
            pattern = settings.get("intake_naming_series") or "INTAKE-.{YYYY}.-.#####"
            self.intake_record_id = naming.make_autoname(pattern, doc=self)
        self.name = self.intake_record_id

    def validate(self) -> None:
        self._enforce_dynamic_mandatory_fields()
        self._sync_info_from_existing_instrument()

    def _enforce_dynamic_mandatory_fields(self) -> None:
        missing = [
            self.meta.get_label(f) for f in MANDATORY_BY_TYPE.get(self.intake_type, set()) if not self.get(f)
        ]
        if missing:
            frappe.throw(
                _(f"Required fields are missing: {', '.join(missing)}"), title=_("Validation Error")
            )

    def _sync_info_from_existing_instrument(self) -> None:
        if self.serial_no and not self.instrument:
            instrument = frappe.db.get_value(
                "Instrument", {"serial_no": self.serial_no}, ["name", "brand", "model", "instrument_category"], as_dict=True
            )
            if instrument:
                self.instrument = instrument["name"]
                if not self.manufacturer:
                    self.manufacturer = instrument["brand"]
                if not self.model:
                    self.model = instrument["model"]
                if not self.instrument_category:
                    self.instrument_category = instrument["instrument_category"]

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
            "instrument_category"
        ],
        as_dict=True,
    )
    if data:
        data["manufacturer"] = data.pop("brand", None)
    return data

@frappe.whitelist()
def get_instrument_inspection_name(intake_record_id: str) -> str | None:
    if not intake_record_id:
        return None
    return frappe.db.get_value("Instrument Inspection", {"intake_record_id": intake_record_id}, "name")
