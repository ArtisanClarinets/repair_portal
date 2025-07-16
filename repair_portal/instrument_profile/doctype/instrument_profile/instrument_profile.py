# File Header Template
# Relative Path: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Last Updated: 2025-07-14
# Version: v1.3
# Purpose: Handles ERPNext Serial No syncing for instruments, and links repair + inspection logs + related trackers
# Dependencies: Serial No (ERPNext), frappe.exceptions, Repair Log, Initial Intake Inspection, Clarinet Inspection, Material Use Log, etc.

import frappe
from frappe.model.document import Document

class InstrumentProfile(Document):
    def on_update(self):
        # Sync with ERPNext Serial No
        try:
            if self.serial_no:
                if not frappe.db.exists("Serial No", self.serial_no):
                    frappe.throw(f"Serial No '{self.serial_no}' does not exist in ERPNext!")
                serial = frappe.get_doc("Serial No", self.serial_no)
        except frappe.DoesNotExistError:
            try:
                serial = frappe.get_doc({
                    "doctype": "Serial No",
                    "serial_no": self.serial_no,
                    "item_code": self.model or "Generic Instrument",
                    "status": "Active"
                })
                serial.insert(ignore_permissions=True)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Serial No insert failed")
        else:
            try:
                if serial.item_code != self.model:
                    frappe.msgprint("ERP Serial No model does not match instrument model.")
            except Exception:
                frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Serial No model mismatch")

        try:
            self.erpnext_serial_no = self.serial_no
        except Exception:
            frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Failed linking Serial No")

        # Auto-populate linked records
        try:
            link_map = [
                ("repair_logs", "Repair Log", {"instrument": self.name}, ["name", "date", "summary"], ["repair_log", "date", "summary"]),
                ("inspection_results", "Initial Intake Inspection", {"instrument_serial": self.serial_no}, ["name", "inspection_date", "model"], ["inspection", "inspection_date", "model"]),
                ("setup_logs", "Clarinet Setup Log", {"instrument": self.name}, ["name", "setup_date", "technician"], ["setup_log", "setup_date", "technician"]),
                ("qa_findings", "Clarinet Inspection", {"instrument": self.name}, ["name", "status"], ["inspection", "status"]),
                ("condition_logs", "Instrument Condition Record", {"instrument": self.name}, ["name", "record_date"], ["condition_record", "record_date"]),
                ("external_work_logs", "External Work Logs", {"instrument": self.name}, ["name", "date"], ["external_log", "date"]),
                ("warranty_logs", "Warranty Modification Log", {"instrument": self.name}, ["name", "modification_type"], ["warranty_log", "modification_type"]),
                ("material_usage", "Material Use Log", {"instrument": self.name}, ["name", "used_on"], ["material_log", "used_on"]),
                ("lab_readings", "Leak Test", {"serial_no": self.serial_no}, ["name", "test_date"], ["test", "test_date"]),
                ("document_history", "Instrument Document History", {"instrument": self.name}, ["name", "entry_type"], ["history_doc", "entry_type"]),
                ("interaction_logs", "Instrument Interaction Log", {"instrument": self.name}, ["name", "interaction_type"], ["interaction", "interaction_type"]),
            ]

            for table_field, doctype, filters, src_fields, target_fields in link_map:
                self.set(table_field, [])
                entries = frappe.get_all(doctype, filters=filters, fields=src_fields)
                for e in entries:
                    self.append(table_field, dict(zip(target_fields, [e[f] for f in src_fields])))

        except Exception:
            frappe.log_error(frappe.get_traceback(), "InstrumentProfile: Failed syncing related child tables")