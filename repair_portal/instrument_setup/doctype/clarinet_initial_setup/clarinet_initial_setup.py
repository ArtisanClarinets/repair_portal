# File: repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py
# Last Updated: 2025-07-04
# Version: v1.4
# Purpose: Complete Clarinet Initial Setup lifecycle (validation, stock handling, status update, PDF generation)
# Dependencies: Frappe >= v15

import frappe
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file

class ClarinetInitialSetup(Document):

    def before_insert(self):
        if not self.technician:
            available = frappe.get_all(
                "User", filters={"role_profile_name": "Technician"}, fields=["name"], limit=1
            )
            if available:
                self.technician = available[0].name

    def validate(self):
        # Enforce checklist completion
        for row in self.checklist:
            if not row.completed:
                frappe.throw("All Setup Checklist Items must be completed before submission.")

        # Enforce at least one Setup Log entry
        if not self.setup_log:
            frappe.throw("At least one Setup Log entry is required for traceability.")

        # Stock validation
        for item in self.materials:
            bin_qty = (
                frappe.db.get_value(
                    "Bin", {"item_code": item.item, "warehouse": item.warehouse}, "actual_qty"
                )
                or 0
            )
            if item.quantity > bin_qty:
                frappe.throw(f"Insufficient stock for item {item.item}")

    def on_submit(self):
        # Create Material Request
        mr = frappe.new_doc("Material Request")
        mr.material_request_type = "Material Transfer"
        for item in self.materials:
            mr.append(
                "items",
                {
                    "item_code": item.item,
                    "qty": item.quantity,
                    "schedule_date": frappe.utils.nowdate(),
                    "warehouse": item.warehouse,
                },
            )
        mr.insert()
        frappe.msgprint(f"Auto-created Material Request: {mr.name}")

        # Auto-finalize Instrument Profile status
        if self.instrument_profile:
            ip = frappe.get_doc("Instrument Profile", self.instrument_profile)
            ip.db_set("status", "Ready for Sale")

        # Enqueue PDF generation (non-blocking)
        frappe.enqueue(
            method="repair_portal.instrument_setup.doctype.clarinet_initial_setup.clarinet_initial_setup.ClarinetInitialSetup._generate_setup_certificate",
            queue='default',
            job_name=f"Generate Setup Certificate for {self.name}",
            doc=self
        )

    def _generate_setup_certificate(self):
        """Render HTML → PDF → attach File (v15-safe)."""
        html = frappe.render_template(
            "repair_portal/templates/clarinet_initial_setup_certificate.html",
            {"doc": self}
        )
        pdf = get_pdf(html)
        fname = f"Setup Certificate - {self.name}.pdf"
        save_file(
            fname,
            pdf,
            self.doctype,
            self.name,
            is_private=1
        )
