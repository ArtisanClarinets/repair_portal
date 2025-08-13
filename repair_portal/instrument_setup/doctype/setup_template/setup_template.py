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
    def validate(self):
        # (Preserved behavior) Auto-create pad_map if missing
        if not self.pad_map and self.clarinet_model:
            pad_map = frappe.get_doc(
                {"doctype": "Clarinet Pad Map", "clarinet_model": self.clarinet_model}
            )
            pad_map.insert(ignore_permissions=True)
            self.pad_map = pad_map.name
            frappe.msgprint(_("Auto-created Pad Map: {0}").format(pad_map.name))

        # Gentle quality checks on template_tasks
        seen = set()
        for row in (self.get("template_tasks") or []):
            if row.sequence in seen:
                frappe.throw(_("Duplicate sequence in Template Tasks: {0}").format(row.sequence))
            seen.add(row.sequence)
            if not row.subject:
                frappe.throw(_("Template Task subject is required (sequence: {0}).").format(row.sequence))
