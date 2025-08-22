# File Header Template
# Relative Path: repair_portal/instrument_setup/doctype/setup_template/setup_template.py
# Last Updated: 2025-07-25
# Version: v1.2
# Purpose: Preserve prior behavior (auto-create Clarinet Pad Map). Add light checks for template tasks.
# Dependencies: Clarinet Pad Map

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class SetupTemplate(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from repair_portal.instrument_setup.doctype.clarinet_setup_operation.clarinet_setup_operation import (
            ClarinetSetupOperation,
        )
        from repair_portal.instrument_setup.doctype.clarinet_template_task.clarinet_template_task import (
            ClarinetTemplateTask,
        )
        from repair_portal.instrument_setup.doctype.setup_checklist_item.setup_checklist_item import (
            SetupChecklistItem,
        )

        checklist_items: DF.Table[SetupChecklistItem]
        clarinet_model: DF.Link
        default_operations: DF.Table[ClarinetSetupOperation]
        default_technician: DF.Link | None
        estimated_cost: DF.Currency
        estimated_hours: DF.Float
        estimated_materials_cost: DF.Currency
        is_active: DF.Check
        pad_map: DF.Link | None
        priority: DF.Literal[Low, Medium, High, Urgent]  # type: ignore
        setup_type: DF.Literal[
            'Standard Setup',
            'Advanced Setup',
            'Repair & Setup',
            'Maintenance',
            'Overhaul',
            'Custom Setup',
        ]
        template_name: DF.Data
        template_tasks: DF.Table[ClarinetTemplateTask]
    # end: auto-generated types

    def validate(self):
        self.validate_template_consistency()
        self.auto_create_pad_map()
        self.validate_template_tasks()
        self.calculate_estimated_cost()

    def validate_template_consistency(self):
        """Ensure template data is consistent and complete."""
        if not self.template_name:
            self.template_name = f'{self.clarinet_model} - {self.setup_type}'

        if not self.setup_type:
            frappe.throw(_('Setup Type is required for project template.'))

    def auto_create_pad_map(self):
        """Auto-create pad_map if missing (preserved behavior)."""
        if not self.pad_map and self.clarinet_model:
            existing = frappe.db.exists('Clarinet Pad Map', {'clarinet_model': self.clarinet_model})
            if existing:
                self.pad_map = existing  # type: ignore
                frappe.msgprint(_('Found existing Pad Map: {0}').format(existing))
            else:
                pad_map = frappe.get_doc(
                    {'doctype': 'Clarinet Pad Map', 'clarinet_model': self.clarinet_model}
                )
                pad_map.insert(ignore_permissions=True)
                self.pad_map = pad_map.name
                frappe.msgprint(_('Auto-created Pad Map: {0}').format(pad_map.name))

    def validate_template_tasks(self):
        """Validate template tasks for consistency."""
        seen = set()
        total_duration = 0

        for row in self.get('template_tasks') or []:
            if row.sequence in seen:
                frappe.throw(_('Duplicate sequence in Template Tasks: {0}').format(row.sequence))
            seen.add(row.sequence)

            if not row.subject:
                frappe.throw(
                    _('Template Task subject is required (sequence: {0}).').format(row.sequence)
                )

            total_duration += row.exp_duration_days or 1

        # Update estimated hours based on task durations (assume 8 hours per day)
        if total_duration > 0 and not self.estimated_hours:
            self.estimated_hours = total_duration * 8

    def calculate_estimated_cost(self):
        """Calculate estimated cost based on hours and materials."""
        if not self.estimated_cost and self.estimated_hours:
            # Assume a standard hourly rate for estimation (this could be configurable)
            hourly_rate = (
                frappe.db.get_single_value('Repair Portal Settings', 'standard_hourly_rate') or 75
            )
            labor_cost = self.estimated_hours * hourly_rate  # type: ignore
            materials_cost = self.estimated_materials_cost or 0
            self.estimated_cost = labor_cost + materials_cost  # type: ignore

    @frappe.whitelist()
    def get_template_summary(self):
        """Return a summary of this template for project creation."""
        return {
            'template_name': self.template_name,
            'setup_type': self.setup_type,
            'estimated_hours': self.estimated_hours,
            'estimated_cost': self.estimated_cost,
            'estimated_materials_cost': self.estimated_materials_cost,
            'default_technician': self.default_technician,
            'priority': self.priority,
            'operations_count': len(self.default_operations or []),
            'checklist_count': len(self.checklist_items or []),
            'tasks_count': len(self.template_tasks or []),
        }
