# Path: repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py
# Version: v3.2
# Date: 2025-08-12
# Purpose: Clarinet Initial Setup lifecycle (Projects-like).
# Adds: generate_certificate() that uses Print Format "Clarinet Setup Certificate"
# Keeps: checklist guarantee, intake requirement, load ops from template, progress roll-up

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, nowdate, now_datetime
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf


PRINT_FORMAT_NAME = "Clarinet Setup Certificate"


class ClarinetInitialSetup(Document):
    # -----------------
    # Lifecycle Hooks
    # -----------------
    def before_insert(self):
        if not self.technician:
            tech = frappe.db.get_value("User", {"role_profile_name": "Technician"}, "name")
            if tech:
                self.technician = tech

        self.ensure_checklist()

        if not self.setup_date:
            self.setup_date = nowdate()

    def validate(self):
        if not self.intake:
            frappe.throw(_("Clarinet Intake reference is required."))
        self.ensure_checklist()

    def on_submit(self):
        # Attach a certificate PDF automatically on submit (best-effort).
        try:
            self.generate_certificate(print_format=PRINT_FORMAT_NAME, attach=1, return_file_url=0)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Clarinet Initial Setup: auto certificate generation failed")

    # -----------------
    # Preserved Utilities
    # -----------------
    def ensure_checklist(self):
        if not self.checklist:
            self.append("checklist", {"task": _("Visual Triage & Safety Check"), "completed": 0})

    @frappe.whitelist()
    def load_operations_from_template(self):
        if not self.setup_template:
            frappe.throw(_("Select a Setup Template first."))

        template = frappe.get_doc("Setup Template", self.setup_template)
        default_ops = list(template.get("default_operations") or [])
        if not default_ops:
            frappe.msgprint(_("No Default Operations found in the selected Setup Template."))
            return

        try:
            for op in default_ops:
                self.append(
                    "operations_performed",
                    {
                        "operation_type": op.operation_type,
                        "section": op.section,
                        "component_ref": op.component_ref,
                        "details": op.details,
                        "completed": 0,
                    },
                )
            self.save()
            frappe.msgprint(_("Loaded {0} operation(s) from template.").format(len(default_ops)))
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Error loading operations from Setup Template")
            frappe.throw(_("Failed to load default operations. Please contact an administrator."))

    # -----------------
    # New: Template → Task creation & Progress Roll-up
    # -----------------
    @frappe.whitelist()
    def create_tasks_from_template(self) -> dict:
        if not self.setup_template:
            frappe.throw(_("Select a Setup Template first."))

        template = frappe.get_doc("Setup Template", self.setup_template)
        rows = sorted(list(template.get("template_tasks") or []), key=lambda r: r.sequence or 0)
        if not rows:
            frappe.msgprint(_("No Template Tasks found on the selected Setup Template."))
            return {"created": [], "count": 0}

        created = []
        for row in rows:
            exp_start = add_days(self.setup_date, row.exp_start_offset_days or 0) if self.setup_date else None
            exp_end = add_days(exp_start, (row.exp_duration_days or 1) - 1) if exp_start else None

            doc = frappe.get_doc(
                {
                    "doctype": "Clarinet Setup Task",
                    "clarinet_initial_setup": self.name,
                    "subject": row.subject,
                    "description": row.description,
                    "priority": row.default_priority or "Medium",
                    "status": "Open",
                    "sequence": row.sequence,
                    "exp_start_date": exp_start,
                    "exp_end_date": exp_end,
                    "instrument": self.instrument,
                    "serial_no": self.serial_no,
                }
            ).insert(ignore_permissions=True)
            created.append(doc.name)

        update_parent_progress(self.name)
        frappe.msgprint(_("Created {0} task(s) from template.").format(len(created)))
        return {"created": created, "count": len(created)}

    # -----------------
    # Certificate (Print Format-backed)
    # -----------------
    @frappe.whitelist()
    def generate_certificate(
        self,
        print_format: str = PRINT_FORMAT_NAME,
        attach: int = 1,
        return_file_url: int = 1
    ):
        """
        Render the configured Print Format and (optionally) attach the PDF to this document.
        Returns {"file_url": "...", "file_name": "..."} when return_file_url is truthy.
        """
        # Ensure print format exists and targets this doctype
        pf = frappe.get_doc("Print Format", print_format) if frappe.db.exists("Print Format", print_format) else None
        if not pf or pf.doc_type != self.doctype:
            frappe.throw(
                _("Print Format '{0}' is missing or not linked to {1}. Reload the print format files.").format(
                    print_format, self.doctype
                )
            )

        # Render HTML via print engine (respects letterheads, permissions, etc.)
        html = frappe.get_print(self.doctype, self.name, print_format)
        pdf_bytes = get_pdf(html)

        # Optionally attach to this document
        filedoc = None
        if attach:
            fname = f"{self.name} - Setup Certificate.pdf"
            filedoc = save_file(fname, pdf_bytes, self.doctype, self.name, is_private=1)

        # Return a download handle (client button can open this)
        if return_file_url:
            out = {"file_url": (filedoc.file_url if filedoc else None), "file_name": (filedoc.file_name if filedoc else None)}
            # If not attached, stream via File doctype (ephemeral) is not available; we require attach=1 for URL.
            if not out["file_url"]:
                # As a fallback, create a File without linkage and return its URL
                fname = f"{self.name} - Setup Certificate.pdf"
                filedoc = frappe.get_doc(
                    {
                        "doctype": "File",
                        "file_name": fname,
                        "is_private": 1,
                        "content": pdf_bytes,
                        "attached_to_doctype": self.doctype,
                        "attached_to_name": self.name,
                    }
                ).insert(ignore_permissions=True)
                out = {"file_url": filedoc.file_url, "file_name": filedoc.file_name}
            return out

        # Nothing to return; just signal success
        return {"ok": True}


@frappe.whitelist()
def update_parent_progress(initial_setup: str):
    tasks = frappe.get_all(
        "Clarinet Setup Task",
        filters={"clarinet_initial_setup": initial_setup},
        fields=["name", "progress"],
    )
    if not tasks:
        frappe.db.set_value("Clarinet Initial Setup", initial_setup, "progress", 0)
        return

    avg = round(sum((t.get("progress") or 0) for t in tasks) / len(tasks), 2)
    frappe.db.set_value("Clarinet Initial Setup", initial_setup, "progress", avg)