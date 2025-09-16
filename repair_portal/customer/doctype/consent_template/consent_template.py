# -*- coding: utf-8 -*-
# File: repair_portal/customer/doctype/consent_template/consent_template.py
# Version: v1.1.0 (2025-09-14)
from __future__ import annotations

import frappe
from frappe.model.document import Document

class ConsentTemplate(Document):
    def validate(self):
        self._ensure_unique_required_labels()

    def _ensure_unique_required_labels(self):
        labels = [frappe.scrub((r.field_label or "").strip()) for r in (self.required_fields or [])]
        seen, dupes = set(), set()
        for x in labels:
            if not x:
                continue
            if x in seen:
                dupes.add(x)
            else:
                seen.add(x)
        if dupes:
            dupes_s = ", ".join(sorted(dupes))
            frappe.throw(f"Duplicate required field labels (case/space-insensitive): {dupes_s}")
