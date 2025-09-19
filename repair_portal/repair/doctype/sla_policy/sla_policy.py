# -*- coding: utf-8 -*-
# Path: repair_portal/repair/doctype/sla_policy/sla_policy.py

from __future__ import annotations

import frappe
from frappe.model.document import Document


class SLAPolicy(Document):
    def validate(self):
        self._validate_thresholds()
        self._validate_rules_present()
        self._dedupe_rules()
        self._normalize_defaults()

    def on_update(self):
        # Ensure single default policy
        if self.default_policy and self.enabled:
            self._unset_other_defaults()

    # ------------------------
    # Internal validations
    # ------------------------
    def _validate_thresholds(self):
        for field in ("warn_threshold_pct", "critical_threshold_pct"):
            val = (self.get(field) or 0)
            if not (0 <= int(val) <= 100):
                frappe.throw(f"{field} must be between 0 and 100.")
        if int(self.warn_threshold_pct or 0) > int(self.critical_threshold_pct or 0):
            frappe.throw("Warn Threshold (%) must be <= Critical Threshold (%).")
        if int(self.breach_grace_minutes or 0) < 0:
            frappe.throw("Breach Grace (Minutes) cannot be negative.")

    def _validate_rules_present(self):
        if not self.rules or len(self.rules) == 0:
            frappe.throw("At least one SLA Policy Rule is required.")

    def _dedupe_rules(self):
        """Ensure no duplicate (service_type, workshop, start_event, stop_event) tuples."""
        seen = set()
        for r in self.rules:
            key = (
                r.service_type or "",
                (r.workshop or "") if self.apply_per_workshop else "",
                r.start_event or "",
                r.stop_event or "",
            )
            if key in seen:
                frappe.throw(
                    "Duplicate SLA Policy Rule detected for "
                    f"Service={r.service_type or '—'}, Workshop={r.workshop or '—'}, "
                    f"Start={r.start_event or '—'}, Stop={r.stop_event or '—'}"
                )
            seen.add(key)

    def _normalize_defaults(self):
        """Disallow disabled default, and ensure only enabled policies can be default."""
        if self.default_policy and not self.enabled:
            frappe.throw("Default Policy must be Enabled.")

    def _unset_other_defaults(self):
        frappe.db.sql(
            """
            UPDATE `tabSLA Policy`
            SET default_policy = 0
            WHERE name != %s AND default_policy = 1
            """,
            (self.name,),
        )
