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
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_setup.doctype.clarinet_setup_operation.clarinet_setup_operation import ClarinetSetupOperation
        from repair_portal.instrument_setup.doctype.setup_checklist_item.setup_checklist_item import SetupChecklistItem
        from repair_portal.instrument_setup.doctype.setup_material_log.setup_material_log import SetupMaterialLog
        from repair_portal.repair_logging.doctype.instrument_interaction_log.instrument_interaction_log import InstrumentInteractionLog

        amended_from: DF.Link | None
        checklist: DF.Table[SetupChecklistItem]
        clarinet_initial_setup_id: DF.Data | None
        clarinet_type: DF.Literal["B\u266d Clarinet", "A Clarinet", "E\u266d Clarinet", "Bass Clarinet", "Alto Clarinet", "Contrabass Clarinet", "Other"]
        inspection: DF.Link | None
        instrument: DF.Link
        instrument_profile: DF.Link | None
        intake: DF.Link | None
        labor_hours: DF.Float
        materials_used: DF.Table[SetupMaterialLog]
        model: DF.Data | None
        notes: DF.Table[InstrumentInteractionLog]
        operations_performed: DF.Table[ClarinetSetupOperation]
        progress: DF.Percent
        serial: DF.Link | None
        setup_date: DF.Date | None
        setup_template: DF.Link | None
        status: DF.Literal["Open", "Pending", "Pass", "Fail"]
        technical_tags: DF.TextEditor | None
        technician: DF.Link | None
        work_photos: DF.AttachImage | None
    # end: auto-generated types
    # -----------------
    # Lifecycle Hooks
    # -----------------
    def before_insert(self):
        self.set_defaults_from_template()
        self.ensure_checklist()
        self.set_project_dates()

    def validate(self):
        if not self.intake:
            frappe.throw(_("Clarinet Intake reference is required."))
        self.ensure_checklist()
        self.validate_project_dates()
        self.calculate_costs()

    def on_update_after_submit(self):
        """Update actual dates based on status changes."""
        self.update_actual_dates()

    def on_submit(self):
        # Mark as completed and set actual end date
        if self.status not in ["Completed", "QA Review"]:
            self.status = "Completed"
        self.actual_end_date = now_datetime()
        
        # Attach a certificate PDF automatically on submit (best-effort).
        try:
            self.generate_certificate(print_format=PRINT_FORMAT_NAME, attach=1, return_file_url=0)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Clarinet Initial Setup: auto certificate generation failed")

    # -----------------
    # Project Management Methods
    # -----------------
    def set_defaults_from_template(self):
        """Set default values from selected template."""
        if self.setup_template:
            template = frappe.get_doc("Setup Template", self.setup_template)
            
            # Set project details from template
            if not self.setup_type:
                self.setup_type = template.setup_type
            if not self.priority:
                self.priority = template.priority
            if not self.technician and template.default_technician:
                self.technician = template.default_technician
            if not self.estimated_cost:
                self.estimated_cost = template.estimated_cost
            if not self.estimated_materials_cost:
                self.estimated_materials_cost = template.estimated_materials_cost
            if not self.labor_hours:
                self.labor_hours = template.estimated_hours

        # Set default technician if not set
        if not self.technician:
            tech = frappe.db.get_value("User", {"role_profile_name": "Technician"}, "name")
            if tech:
                self.technician = tech

    def set_project_dates(self):
        """Set project timeline dates."""
        if not self.setup_date:
            self.setup_date = nowdate()
        
        if not self.expected_start_date:
            self.expected_start_date = self.setup_date
            
        # Set expected end date based on estimated hours
        if not self.expected_end_date and self.labor_hours:
            # Assume 8 hours per day
            days_needed = max(1, int((self.labor_hours or 0) / 8))
            self.expected_end_date = add_days(self.expected_start_date, days_needed)

    def validate_project_dates(self):
        """Validate project timeline consistency."""
        if self.expected_start_date and self.expected_end_date:
            if self.expected_end_date < self.expected_start_date:
                frappe.throw(_("Expected End Date cannot be before Expected Start Date."))
        
        if self.actual_start_date and self.actual_end_date:
            if self.actual_end_date < self.actual_start_date:
                frappe.throw(_("Actual End Date cannot be before Actual Start Date."))

    def update_actual_dates(self):
        """Update actual dates based on status."""
        if self.status == "In Progress" and not self.actual_start_date:
            self.actual_start_date = now_datetime()
        elif self.status in ["Completed", "QA Review"] and not self.actual_end_date:
            self.actual_end_date = now_datetime()

    def calculate_costs(self):
        """Calculate actual costs from materials used."""
        materials_total = 0
        for material in (self.materials_used or []):
            materials_total += (material.amount or 0)
        
        self.actual_materials_cost = materials_total
        
        # Calculate labor cost if hourly rate is available
        if self.labor_hours:
            hourly_rate = frappe.db.get_single_value("Repair Portal Settings", "standard_hourly_rate") or 75
            labor_cost = self.labor_hours * hourly_rate
            self.actual_cost = labor_cost + materials_total

    # -----------------
    # Preserved Utilities
    # -----------------
    def ensure_checklist(self):
        if not self.checklist:
            self.append("checklist", {"task": _("Visual Triage & Safety Check"), "completed": 0})

    @frappe.whitelist()
    def load_operations_from_template(self):
        """Load default operations from the selected setup template."""
        if not self.setup_template:
            frappe.throw(_("Select a Setup Template first."))

        template = frappe.get_doc("Setup Template", self.setup_template)
        
        # Apply template defaults if not already set
        if not self.setup_type and template.setup_type:
            self.setup_type = template.setup_type
        if not self.priority and template.priority:
            self.priority = template.priority
        if not self.estimated_cost and template.estimated_cost:
            self.estimated_cost = template.estimated_cost
        if not self.estimated_materials_cost and template.estimated_materials_cost:
            self.estimated_materials_cost = template.estimated_materials_cost
        
        # Load default operations
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
            
            # Load checklist items
            for item in (template.get("checklist_items") or []):
                self.append(
                    "checklist",
                    {
                        "task": item.task,
                        "completed": item.completed,
                        "notes": item.notes
                    }
                )
                
            self.save()
            frappe.msgprint(_("Loaded {0} operation(s) and {1} checklist item(s) from template.").format(
                len(default_ops), len(template.get("checklist_items") or [])
            ))
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Error loading operations from Setup Template")
            frappe.throw(_("Failed to load default operations. Please contact an administrator."))

    # -----------------
    # New: Template → Task creation & Progress Roll-up
    # -----------------
    @frappe.whitelist()
    def create_tasks_from_template(self) -> dict:
        """Create project tasks from the template task blueprints."""
        if not self.setup_template:
            frappe.throw(_("Select a Setup Template first."))

        template = frappe.get_doc("Setup Template", self.setup_template)
        rows = sorted(list(template.get("template_tasks") or []), key=lambda r: r.sequence or 0)
        if not rows:
            frappe.msgprint(_("No Template Tasks found on the selected Setup Template."))
            return {"created": [], "count": 0}

        # Use expected_start_date if available, otherwise use setup_date
        base_date = self.expected_start_date or self.setup_date
        if not base_date:
            frappe.throw(_("Expected Start Date or Setup Date is required to create tasks."))

        created = []
        for row in rows:
            exp_start = add_days(base_date, row.exp_start_offset_days or 0)
            exp_end = add_days(exp_start, (row.exp_duration_days or 1) - 1)

            doc = frappe.get_doc(
                {
                    "doctype": "Clarinet Setup Task",
                    "clarinet_initial_setup": self.name,
                    "subject": row.subject,
                    "description": row.description,
                    "priority": row.default_priority or self.priority or "Medium",
                    "status": "Open",
                    "sequence": row.sequence,
                    "exp_start_date": exp_start,
                    "exp_end_date": exp_end,
                    "instrument": self.instrument,
                    "serial": self.serial,
                }
            ).insert(ignore_permissions=True)
            created.append(doc.name)

        # Update project progress
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