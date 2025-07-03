# relative path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# last updated: 2025-07-03
# version: 1.3
# purpose: Controller for Clarinet Intake — links ERPNext documents for inventory traceability, enforces intake requirements, and launches QC/inspection workflows for new and repaired instruments.
# notes: Adds logic to clear Hold stock status when QC passes; fully aligns with repair_portal compliance and agent review findings.

from __future__ import annotations

import frappe
from frappe.model.document import Document

from . import clarinet_intake_block_flagged


class ClarinetIntake(Document):
    def validate(self):
        """Ensure required fields per Intake Type, then sync Instrument Profile."""
        self._validate_required_fields()
        self._ensure_purchase_receipt()
        self._ensure_item()
        self._ensure_instrument_profile()
        self._ensure_quality_inspection()
        self._sync_instrument_profile()

    def before_save(self):
        clarinet_intake_block_flagged.before_save(self)

    def before_cancel(self):
        clarinet_intake_block_flagged.before_cancel(self)

    def before_submit(self):
        if self.intake_type == "Inventory" and self.qc_status == "Fail":
            frappe.throw("QC Failed — resolve QC before submitting this Intake.")

    def on_submit(self):
        if self.intake_type != "Inventory":
            return
        self._ensure_item()
        self._ensure_serial_no()
        self._ensure_quality_inspection()
        self._sync_instrument_profile()

    def on_update(self):
        if self.has_value_changed("stock_status"):
            self._update_profile_stock_status()
        if self.has_value_changed("qc_status"):
            self._apply_qc_hold()
            self._release_qc_hold_if_passed()

    def _validate_required_fields(self):
        if self.intake_type == "Inventory":
            for fld in ("purchase_order", "purchase_receipt", "warehouse"):
                if not self.get(fld):
                    frappe.throw(
                        frappe._("{0} is required for Inventory Intakes").format(
                            fld.replace("_", " ").title()
                        )
                    )
        elif self.intake_type == "Repair":
            for fld in ("customer", "due_date"):
                if not self.get(fld):
                    frappe.throw(
                        frappe._("{0} is required for Repair Intakes").format(fld.replace("_", " ").title())
                    )

    def _ensure_purchase_receipt(self):
        """Auto-create or link a Purchase Receipt if missing for Inventory Intake."""
        if self.intake_type != "Inventory":
            return
        if not self.purchase_receipt:
            # Try to find existing Purchase Receipt for item/serial
            pr = frappe.db.get_value(
                "Purchase Receipt Item",
                {"item_code": self.item_code, "serial_no": self.serial_number},
                "parent",
            )
            if pr:
                self.purchase_receipt = pr
                return
            # Auto-create Purchase Receipt if not found (minimal viable)
            pr_doc = frappe.new_doc("Purchase Receipt")
            pr_doc.supplier = self.supplier or "Unknown"
            pr_doc.append(
                "items",
                {
                    "item_code": self.item_code,
                    "qty": 1,
                    "warehouse": self.warehouse,
                    "serial_no": self.serial_number,
                },
            )
            pr_doc.save()
            self.purchase_receipt = pr_doc.name

    def _ensure_item(self):
        if not frappe.db.exists("Item", self.item_code):
            item = frappe.new_doc("Item")
            item.item_code = self.item_code
            item.item_name = self.item_name or self.item_code
            item.item_group = "Clarinets"
            item.is_stock_item = 1
            item.has_serial_no = 1
            item.stock_uom = "Nos"
            item.save()

    def _ensure_serial_no(self):
        if not frappe.db.exists("Serial No", self.serial_number):
            serial = frappe.new_doc("Serial No")
            serial.serial_no = self.serial_number
            serial.item_code = self.item_code
            serial.warehouse = self.warehouse
            serial.status = "Active"
            serial.purchase_document_type = "Purchase Receipt"
            serial.purchase_document_no = self.purchase_receipt
            serial.save()

    def _ensure_instrument_profile(self):
        if not self.instrument_profile:
            # Try to find Instrument Profile by serial number
            ip = frappe.db.get_value("Instrument Profile", {"serial_number": self.serial_number})
            if ip:
                self.instrument_profile = ip
                return
            # Auto-create Instrument Profile
            ip_doc = frappe.new_doc("Instrument Profile")
            ip_doc.serial_number = self.serial_number
            ip_doc.model = self.item_name
            ip_doc.item_code = self.item_code
            ip_doc.status = self.stock_status or "New Intake"
            ip_doc.latest_intake = self.name
            ip_doc.save()
            self.instrument_profile = ip_doc.name

    def _ensure_quality_inspection(self):
        if self.intake_type != "Inventory":
            return
        # Create ERPNext Quality Inspection if not already
        qi_exists = frappe.db.exists(
            "Quality Inspection",
            {
                "reference_type": "Purchase Receipt",
                "reference_name": self.purchase_receipt,
                "item_code": self.item_code,
                "inspection_type": "Incoming",
            },
        )
        if qi_exists:
            return
        qi_doc = frappe.new_doc("Quality Inspection")
        qi_doc.inspection_type = "Incoming"
        qi_doc.reference_type = "Purchase Receipt"
        qi_doc.reference_name = self.purchase_receipt
        qi_doc.item_code = self.item_code
        qi_doc.sample_size = 1
        qi_doc.report_date = frappe.utils.nowdate()
        qi_doc.save()

    def _sync_instrument_profile(self):
        if not self.instrument_profile:
            return
        inst = frappe.get_doc("Instrument Profile", self.instrument_profile)
        if self.intake_type == "Inventory":
            inst.db_set("status", self.stock_status)
        else:
            inst.db_set("status", "Under Repair")
        inst.db_set("latest_intake", self.name)
        inst.save(ignore_permissions=True)

    def _update_profile_stock_status(self):
        inst = frappe.get_doc("Instrument Profile", self.instrument_profile)
        inst.db_set("status", self.stock_status)
        inst.save(ignore_permissions=True)

    def _apply_qc_hold(self):
        if self.intake_type == "Inventory" and self.qc_status == "Fail":
            self.db_set("stock_status", "Hold")

    def _release_qc_hold_if_passed(self):
        if (
            self.intake_type == "Inventory"
            and self.qc_status == "Pass"
            and self.stock_status == "Hold"
        ):
            self.db_set("stock_status", "Available")
