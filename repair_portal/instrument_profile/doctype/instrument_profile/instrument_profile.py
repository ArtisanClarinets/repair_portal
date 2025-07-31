# File Header Template
# Relative Path: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Last Updated: 2025-07-19
# Version: v1.7
# Purpose: Handles ERPNext Serial No syncing for instruments, warranty expiration sync, and links repair + inspection logs + related trackers
# Dependencies: Serial No (ERPNext), frappe.exceptions, Repair Log, Instrument Inspection, Material Use Log, etc.

"""
InstrumentProfile Controller
---------------------------
Ensures every Instrument Profile is linked to an ERPNext Serial No, and auto-syncs all related logs (repairs, inspections, setups, QA, etc.) as child tables. Now also syncs warranty expiration from Serial No for dashboard use.

Compliant with:
- Frappe/ERPNext v15 best practices
- Fortune 500 error handling and audit
- Audit trail and data integrity

Changes (2025-07-19):
- Replaced all references to Clarinet Inspection and Initial Intake Inspection with Instrument Inspection
"""

import frappe
from frappe.model.document import Document


class InstrumentProfile(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_profile.doctype.external_work_logs.external_work_logs import ExternalWorkLogs
        from repair_portal.instrument_profile.doctype.instrument_accessory.instrument_accessory import InstrumentAccessory
        from repair_portal.instrument_profile.doctype.instrument_condition_record.instrument_condition_record import InstrumentConditionRecord
        from repair_portal.instrument_profile.doctype.instrument_photo.instrument_photo import InstrumentPhoto
        from repair_portal.repair_logging.doctype.instrument_interaction_log.instrument_interaction_log import InstrumentInteractionLog
        from repair_portal.repair_logging.doctype.material_use_log.material_use_log import MaterialUseLog
        from repair_portal.repair_logging.doctype.warranty_modification_log.warranty_modification_log import WarrantyModificationLog

        accessory_log: DF.Table[InstrumentAccessory]
        amended_from: DF.Link | None
        body_material: DF.Data | None
        bore_measurement: DF.Float
        bore_style: DF.Data | None
        brand: DF.Data | None
        condition_logs: DF.Table[InstrumentConditionRecord]
        current_location: DF.Data | None
        current_status: DF.Literal["For Sale", "In Workshop", "With Customer", "Sold", "Archived"]
        external_work_logs: DF.Table[ExternalWorkLogs]
        initial_condition_notes: DF.Text | None
        instrument: DF.Link
        instrument_category: DF.Data | None
        instrument_profile_id: DF.Data | None
        intake_date: DF.Date | None
        interaction_logs: DF.Table[InstrumentInteractionLog]
        key_plating: DF.Data | None
        key_system: DF.Literal["Boehm", "Albert", "Oehler", "Other"]
        linked_inspection: DF.Link | None
        material_usage: DF.Table[MaterialUseLog]
        model: DF.Data | None
        number_of_keys_rings: DF.Data | None
        pad_type_current: DF.Data | None
        pitch_standard: DF.Data | None
        profile_image: DF.AttachImage | None
        purchase_order: DF.Link | None
        purchase_receipt: DF.Link | None
        serial_no: DF.Link | None
        serial_photos: DF.Table[InstrumentPhoto]
        service_photos: DF.Table[InstrumentPhoto]
        spring_type: DF.Data | None
        thumb_rest: DF.Data | None
        tone_hole_style: DF.Data | None
        warranty_expiration: DF.Date | None
        warranty_logs: DF.Table[WarrantyModificationLog]
        wood_type: DF.Data | None
        workflow_state: DF.Literal["Open", "In Progress", "Delivered", "Archived"]
    # end: auto-generated types
    def on_update(self) -> None:
        """
        Sync Serial No, warranty expiration, and populate all related logs as child tables for UI and audit.
        """
        # Sync with ERPNext Serial No
        try:
            if self.serial_no:
                if not frappe.db.exists("Serial No", self.serial_no):
                    frappe.throw(f"Serial No '{self.serial_no}' does not exist in ERPNext!")
                serial = frappe.get_doc("Serial No", self.serial_no)
                if serial.item_code != getattr(self, "model", None):
                    frappe.msgprint("ERP Serial No model does not match instrument model.")
        except frappe.DoesNotExistError:
            try:
                serial = frappe.get_doc(
                    {
                        "doctype": "Serial No",
                        "serial_no": self.serial_no,
                        "item_code": getattr(self, "model", "Generic Instrument"),
                        "status": "Active",
                    }
                )
                serial.insert(ignore_permissions=True)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Serial No insert failed")
        except Exception:
            frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Serial No sync failed")

        # Ensure ERPNext Serial No is always referenced
        try:
            self.erpnext_serial_no = self.serial_no
        except Exception:
            frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Failed linking Serial No")

        # --- New: Sync warranty_expiration from Serial No ---
        try:
            if self.serial_no:
                warranty = frappe.db.get_value("Serial No", self.serial_no, "warranty_expiry_date")
                if warranty:
                    self.warranty_expiration = warranty
        except Exception:
            frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Warranty Expiration Sync Failed")

        # Auto-populate linked records
        link_map = [
            (
                "repair_logs",
                "Repair Log",
                {"instrument": self.name},
                ["name", "date", "summary"],
                ["repair_log", "date", "summary"],
            ),
            (
                "inspection_results",
                "Instrument Inspection",
                {"instrument_serial": self.serial_no},
                ["name", "inspection_date", "model"],
                ["inspection", "inspection_date", "model"],
            ),
            (
                "setup_logs",
                "Clarinet Setup Log",
                {"instrument": self.name},
                ["name", "setup_date", "technician"],
                ["setup_log", "setup_date", "technician"],
            ),
            (
                "qa_findings",
                "Instrument Inspection",
                {"instrument": self.name},
                ["name", "status"],
                ["inspection", "status"],
            ),
            (
                "condition_logs",
                "Instrument Condition Record",
                {"instrument": self.name},
                ["name", "record_date"],
                ["condition_record", "record_date"],
            ),
            (
                "external_work_logs",
                "External Work Logs",
                {"instrument": self.name},
                ["name", "date"],
                ["external_log", "date"],
            ),
            (
                "warranty_logs",
                "Warranty Modification Log",
                {"instrument": self.name},
                ["name", "modification_type"],
                ["warranty_log", "modification_type"],
            ),
            (
                "material_usage",
                "Material Use Log",
                {"instrument": self.name},
                ["name", "used_on"],
                ["material_log", "used_on"],
            ),
            (
                "lab_readings",
                "Leak Test",
                {"serial_no": self.serial_no},
                ["name", "test_date"],
                ["test", "test_date"],
            ),
            (
                "document_history",
                "Instrument Document History",
                {"instrument": self.name},
                ["name", "entry_type"],
                ["history_doc", "entry_type"],
            ),
            (
                "interaction_logs",
                "Instrument Interaction Log",
                {"instrument": self.name},
                ["name", "interaction_type"],
                ["interaction", "interaction_type"],
            ),
        ]

        for table_field, doctype, filters, src_fields, target_fields in link_map:
            try:
                self.set(table_field, [])
                entries = frappe.get_all(doctype, filters=filters, fields=src_fields)
                for e in entries:
                    self.append(
                        table_field, dict(zip(target_fields, [e[f] for f in src_fields], strict=False))
                    )
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(), f"InstrumentProfile: Failed syncing table {table_field}"
                )
