# Path: repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py
# Version: v3.3
# Date: 2025-09-16
# Purpose: Clarinet Initial Setup lifecycle (minutes-aware, template-driven).
# Notes:
#   - Loads defaults from Setup Template (server) and supports on-form reload (client)
#   - Creates Clarinet Setup Tasks from template with minutes-based durations
#   - Reads hours_per_day and standard_hourly_rate from Repair Portal Settings (with safe defaults)

from __future__ import annotations

from math import ceil
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, now_datetime, nowdate
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf

PRINT_FORMAT_NAME = 'Clarinet Setup Certificate'


def _get_setting(field: str, default: float | int) -> float:
    """
    Safely fetch a numeric single-value setting. Accepts int/float and numeric strings.
    Returns the default for None, empty string, non-numeric strings, or unsupported types
    such as date/datetime to avoid passing them to float().
    """
    from typing import Any
    from datetime import date, datetime, timedelta

    try:
        val: Any = frappe.db.get_single_value('Repair Portal Settings', field)
        if val is None or val == '':
            return float(default)

        # Numeric types are accepted directly
        if isinstance(val, (int, float)):
            return float(val)

        # Try numeric strings
        if isinstance(val, str):
            try:
                return float(val)
            except ValueError:
                return float(default)

        # For dates/datetimes/timedeltas or any other unsupported type, return default
        if isinstance(val, (date, datetime, timedelta)):
            return float(default)

        # Fallback for unexpected types
        return float(default)
    except Exception:
        return float(default)


class ClarinetInitialSetup(Document):
    # begin: auto-generated types (keep)
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_setup.doctype.clarinet_setup_operation.clarinet_setup_operation import ClarinetSetupOperation
        from repair_portal.instrument_setup.doctype.setup_checklist_item.setup_checklist_item import SetupChecklistItem
        from repair_portal.instrument_setup.doctype.setup_material_log.setup_material_log import SetupMaterialLog
        from repair_portal.repair_logging.doctype.instrument_interaction_log.instrument_interaction_log import InstrumentInteractionLog

        actual_cost: DF.Currency
        actual_end_date: DF.Datetime | None
        actual_materials_cost: DF.Currency
        actual_start_date: DF.Datetime | None
        amended_from: DF.Link | None
        checklist: DF.Table[SetupChecklistItem]
        clarinet_initial_setup_id: DF.Data | None
        clarinet_type: DF.Literal['B♭ Clarinet','A Clarinet','E♭ Clarinet','Bass Clarinet','Alto Clarinet','Contrabass Clarinet','Other']
        estimated_cost: DF.Currency
        estimated_materials_cost: DF.Currency
        expected_end_date: DF.Date | None
        expected_start_date: DF.Date | None
        inspection: DF.Link | None
        instrument: DF.Link
        instrument_profile: DF.Link | None
        intake: DF.Link | None
        labor_hours: DF.Float
        materials_used: DF.Table[SetupMaterialLog]
        model: DF.Data | None
        notes: DF.Table[InstrumentInteractionLog]
        operations_performed: DF.Table[ClarinetSetupOperation]
        priority: DF.Literal['Low','Medium','High','Urgent']
        progress: DF.Percent
        serial: DF.Link | None
        setup_date: DF.Date | None
        setup_template: DF.Link | None
        setup_type: DF.Literal['Standard Setup','Advanced Setup','Repair & Setup','Custom Setup']
        status: DF.Literal['Open','In Progress','Completed','On Hold','Cancelled','QA Review','Customer Approval']
        technical_tags: DF.TextEditor | None
        technician: DF.Link | None
        work_photos: DF.AttachImage | None
    # end: auto-generated types

    # -----------------
    # Lifecycle Hooks
    # -----------------
    def before_insert(self):
        # Server-side defaults on brand-new docs
        self.set_defaults_from_template()
        self.ensure_checklist()
        self.set_project_dates()

    def validate(self):
        if not self.intake:
            frappe.throw(_('Clarinet Intake reference is required.'))
        self.ensure_checklist()
        self.validate_project_dates()
        self.calculate_costs()

    def on_update_after_submit(self):
        """Update actual dates based on status changes."""
        self.update_actual_dates()

    def on_submit(self):
        # Mark as completed and set actual end date
        if self.status not in ['Completed', 'QA Review']:
            self.status = 'Completed'
        self.actual_end_date = now_datetime()

        # Best-effort: attach a certificate PDF on submit.
        try:
            self.generate_certificate(print_format=PRINT_FORMAT_NAME, attach=1, return_file_url=0)
        except Exception:
            frappe.log_error(frappe.get_traceback(), 'Clarinet Initial Setup: auto certificate generation failed')

    # -----------------
    # Project Management Methods
    # -----------------
    def set_defaults_from_template(self):
        """Set default values from selected template (server-side)."""
        if self.setup_template:
            template = frappe.get_doc('Setup Template', self.setup_template)  # type: ignore

            if not self.setup_type:
                self.setup_type = template.setup_type  # type: ignore
            if not self.priority:
                self.priority = template.priority  # type: ignore
            if not self.technician and template.default_technician:  # type: ignore
                self.technician = template.default_technician  # type: ignore
            if not self.estimated_cost:
                self.estimated_cost = template.estimated_cost  # type: ignore
            if not self.estimated_materials_cost:
                self.estimated_materials_cost = template.estimated_materials_cost  # type: ignore
            if not self.labor_hours:
                self.labor_hours = template.estimated_hours  # type: ignore
        # If still no tech, try default tech
        if not self.technician:
            tech = frappe.db.get_value('User', {'role_profile_name': 'Technician'}, 'name')
            if tech:
                self.technician = tech  # type: ignore
    # (Reference: your existing defaults loader)  # :contentReference[oaicite:5]{index=5}

    def set_project_dates(self):
        """Set project timeline dates. Uses hours_per_day setting."""
        if not self.setup_date:
            self.setup_date = nowdate()
        if not self.expected_start_date:
            self.expected_start_date = self.setup_date

        # Set expected end based on labor hours
        if not self.expected_end_date and self.labor_hours:
            hours_per_day = _get_setting('hours_per_day', 8)
            days_needed = max(1, ceil(float(self.labor_hours) / max(1.0, hours_per_day)))
            self.expected_end_date = add_days(self.expected_start_date, days_needed)

    def validate_project_dates(self):
        """Validate project timeline consistency."""
        if self.expected_start_date and self.expected_end_date:
            if self.expected_end_date < self.expected_start_date:  # type: ignore
                frappe.throw(_('Expected End Date cannot be before Expected Start Date.'))

        if self.actual_start_date and self.actual_end_date:
            if self.actual_end_date < self.actual_start_date:  # type: ignore
                frappe.throw(_('Actual End Date cannot be before Actual Start Date.'))

    def update_actual_dates(self):
        """Update actual dates based on status."""
        if self.status == 'In Progress' and not self.actual_start_date:
            self.actual_start_date = now_datetime()
        elif self.status in ['Completed', 'QA Review'] and not self.actual_end_date:
            self.actual_end_date = now_datetime()

    def calculate_costs(self):
        """Calculate actual costs from materials used + labor hours."""
        materials_total = 0
        for material in self.materials_used or []:
            materials_total += material.amount or 0

        self.actual_materials_cost = materials_total

        if self.labor_hours:
            hourly_rate = _get_setting('standard_hourly_rate', 75)
            labor_cost = float(self.labor_hours) * hourly_rate  # type: ignore
            self.actual_cost = labor_cost + materials_total  # type: ignore

    # -----------------
    # Preserved Utilities
    # -----------------
    def ensure_checklist(self):
        if not self.checklist:
            self.append('checklist', {'task': _('Visual Triage & Safety Check'), 'completed': 0})

    @frappe.whitelist()
    def load_operations_from_template(self):
        """Load default operations and checklist from the selected setup template."""
        if not self.setup_template:
            frappe.throw(_('Select a Setup Template first.'))

        template = frappe.get_doc('Setup Template', self.setup_template)  # type: ignore

        # Apply template defaults if not already set (client does this too)
        if not self.setup_type and template.setup_type:  # type: ignore
            self.setup_type = template.setup_type  # type: ignore
        if not self.priority and template.priority:  # type: ignore
            self.priority = template.priority  # type: ignore
        if not self.estimated_cost and template.estimated_cost:  # type: ignore
            self.estimated_cost = template.estimated_cost  # type: ignore
        if not self.estimated_materials_cost and template.estimated_materials_cost:  # type: ignore
            self.estimated_materials_cost = template.estimated_materials_cost  # type: ignore

        default_ops = list(template.get('default_operations') or [])
        if not default_ops:
            frappe.msgprint(_('No Default Operations found in the selected Setup Template.'))
            return

        try:
            for op in default_ops:
                self.append('operations_performed', {
                    'operation_type': op.operation_type,
                    'section': op.section,
                    'component_ref': op.component_ref,
                    'details': op.details,
                    'completed': 0,
                })
            for item in template.get('checklist_items') or []:
                self.append('checklist', {
                    'task': item.task,
                    'completed': item.completed,
                    'notes': item.notes,
                })

            self.save()
            frappe.msgprint(_('Loaded {0} operation(s) and {1} checklist item(s) from template.')
                            .format(len(default_ops), len(template.get('checklist_items') or [])))
        except Exception:
            frappe.log_error(frappe.get_traceback(), 'Error loading operations from Setup Template')
            frappe.throw(_('Failed to load default operations. Please contact an administrator.'))
    # (Reference: your existing loader)  # :contentReference[oaicite:6]{index=6}

    # -----------------
    # Template → Task creation (MINUTES-BASED)
    # -----------------
    @frappe.whitelist()
    def create_tasks_from_template(self) -> dict:
        """
        Create Clarinet Setup Task docs from the linked Setup Template.
        - Uses exp_duration_mins primarily; falls back to exp_duration_days for legacy rows.
        - Maps minutes to calendar dates:
            span_days = max(1, ceil(minutes / 1440))
            exp_end_date = exp_start_date + (span_days - 1)
        """
        if not self.setup_template:
            frappe.throw(_('Select a Setup Template first.'))

        template = frappe.get_doc('Setup Template', self.setup_template)  # type: ignore
        rows = sorted(list(template.get('template_tasks') or []), key=lambda r: r.sequence or 0)
        if not rows:
            frappe.msgprint(_('No Template Tasks found on the selected Setup Template.'))
            return {'created': [], 'count': 0}

        base_date = self.expected_start_date or self.setup_date
        if not base_date:
            frappe.throw(_('Expected Start Date or Setup Date is required to create tasks.'))

        created = []
        for row in rows:
            # Offsets remain in DAYS
            exp_start = add_days(base_date, int(getattr(row, 'exp_start_offset_days', 0) or 0))

            minutes = int(getattr(row, 'exp_duration_mins', 0) or 0)
            if minutes > 0:
                span_days = max(1, ceil(minutes / 1440.0))  # 1440 mins/day
            else:
                # Legacy fallback
                days = int(getattr(row, 'exp_duration_days', 0) or 1)
                span_days = max(1, days)

            exp_end = add_days(exp_start, span_days - 1)

            doc = frappe.get_doc({
                'doctype': 'Clarinet Setup Task',
                'clarinet_initial_setup': self.name,
                'subject': row.subject,
                'description': row.description,
                'priority': (row.default_priority or self.priority or 'Medium'),
                'status': 'Open',
                'sequence': row.sequence,
                'exp_start_date': exp_start,
                'exp_end_date': exp_end,
                'instrument': self.instrument,
                'serial': self.serial,
            }).insert(ignore_permissions=True)
            created.append(doc.name)

    #    update_parent_progress(self.name)  # type: ignore
    #    frappe.msgprint(_('Created {0} task(s) from template.').format(len(created)))
    #    return {'created': created, 'count': len(created)}
    # (Reference: your original create-tasks entry point)  # :contentReference[oaicite:7]{index=7}

    # -----------------
    # Certificate (Print Format-backed)
    # -----------------
    @frappe.whitelist()
    def generate_certificate(self, print_format: str = PRINT_FORMAT_NAME, attach: int = 1, return_file_url: int = 1):
        """Render the Print Format and (optionally) attach the PDF; return a URL when requested."""
        pf = (frappe.get_doc('Print Format', print_format)
              if frappe.db.exists('Print Format', print_format) else None)
        if not pf or pf.doc_type != self.doctype:  # type: ignore
            frappe.throw(_("Print Format '{0}' is missing or not linked to {1}. Reload the print format files.")
                         .format(print_format, self.doctype))

        html = frappe.get_print(self.doctype, self.name, print_format)
        pdf_bytes = get_pdf(html)

        filedoc = None
        if attach:
            fname = f'{self.name} - Setup Certificate.pdf'
            filedoc = save_file(fname, pdf_bytes, self.doctype, self.name, is_private=1)

        if return_file_url:
            out = {
                'file_url': (filedoc.file_url if filedoc else None),  # type: ignore
                'file_name': (filedoc.file_name if filedoc else None),  # type: ignore
            }
            if not out['file_url']:
                fname = f'{self.name} - Setup Certificate.pdf'
                filedoc = frappe.get_doc({
                    'doctype': 'File',
                    'file_name': fname,
                    'is_private': 1,
                    'content': pdf_bytes,
                    'attached_to_doctype': self.doctype,
                    'attached_to_name': self.name,
                }).insert(ignore_permissions=True)
                out = {'file_url': filedoc.file_url, 'file_name': filedoc.file_name}  # type: ignore
            return out

        return {'ok': True}


@frappe.whitelist()
def update_parent_progress(initial_setup: str):
    tasks = frappe.get_all('Clarinet Setup Task',
                           filters={'clarinet_initial_setup': initial_setup},
                           fields=['name', 'progress'])
    if not tasks:
        frappe.db.set_value('Clarinet Initial Setup', initial_setup, 'progress', 0)
        return

    avg = round(sum((t.get('progress') or 0) for t in tasks) / len(tasks), 2)
    frappe.db.set_value('Clarinet Initial Setup', initial_setup, 'progress', avg)
