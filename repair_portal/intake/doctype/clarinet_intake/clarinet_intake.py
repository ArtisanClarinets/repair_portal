from __future__ import annotations

import frappe
from frappe.model.document import Document

from . import clarinet_intake_block_flagged


class ClarinetIntake(Document):
    def validate(self):
        """Ensure required fields per Intake Type, then sync Instrument Profile."""
        self._validate_required_fields()
        self._sync_instrument_profile()

    def before_save(self):
        """Block edits if in Flagged state."""
        clarinet_intake_block_flagged.before_save(self)

    def before_cancel(self):
        """Block cancellation if in Flagged state."""
        clarinet_intake_block_flagged.before_cancel(self)

    def before_submit(self):
        """Prevent submission of a failed-QC Inventory intake."""
        if self.intake_type == "Inventory" and self.qc_status == "Fail":
            frappe.throw("QC Failed — resolve QC before submitting this Intake.")

    def on_submit(self):
        """
        Create Item and Serial No when submitting Inventory Intake.
        """
        if self.intake_type != "Inventory":
            return

        if not frappe.db.exists("Item", self.item_code):
            item = frappe.new_doc("Item")
            item.item_code = self.item_code
            item.item_name = self.item_name or self.item_code
            item.item_group = "Clarinets"
            item.is_stock_item = 1
            item.has_serial_no = 1
            item.stock_uom = "Nos"
            item.insert()

        if not frappe.db.exists("Serial No", self.serial_number):
            serial = frappe.new_doc("Serial No")
            serial.serial_no = self.serial_number
            serial.item_code = self.item_code
            serial.warehouse = self.warehouse
            serial.status = "Active"
            serial.purchase_document_type = "Purchase Receipt"
            serial.purchase_document_no = self.purchase_receipt
            serial.insert()

    def on_update(self):
        """React to status changes post-save."""
        if self.has_value_changed("stock_status"):
            self._update_profile_stock_status()
        if self.has_value_changed("qc_status"):
            self._apply_qc_hold()

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

    def _sync_instrument_profile(self):
        """Push Intake info into the linked Instrument Profile."""
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
