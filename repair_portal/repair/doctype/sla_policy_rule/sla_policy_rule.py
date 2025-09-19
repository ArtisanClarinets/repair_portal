# -*- coding: utf-8 -*-
# Path: repair_portal/repair/doctype/sla_policy_rule/sla_policy_rule.py

from __future__ import annotations

import frappe
from frappe.model.document import Document


class SLAPolicyRule(Document):
    def validate(self):
        if (self.tat_hours or 0) <= 0:
            frappe.throw("Turnaround (Hours) must be a positive integer.")
        for fld in ("escalation_minutes_1", "escalation_minutes_2"):
            val = self.get(fld)
            if val is not None and int(val) < 0:
                frappe.throw(f"{fld} cannot be negative.")
