# -*- coding: utf-8 -*-
"""
File: repair_portal/customer/doctype/consent_form/consent_form.py
Version: v2.0.0 (2025-09-14)

Consent Form (canonical):
- Jinja-based rendering from Consent Template.content
- Auto-fills missing values from "Consent Settings" mappings + template defaults
- Enforces: draft allowed without signature; signature required before Submit
- Keeps parity between Template.required_fields and child table values
- Locks key fields post-submit; keeps status/workflow_state consistent
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, nowdate

def _get_settings() -> Optional[Document]:
    if frappe.db.exists("DocType", "Consent Settings"):
        try:
            return frappe.get_single("Consent Settings")
        except Exception:
            return None
    return None

class ConsentForm(Document):
    # Events ---------------------------------------------------------------

    def before_insert(self):
        self._ensure_required_fields()

    def validate(self):
        # Keep child table in sync with template
        self._ensure_required_fields()
        # Apply auto-fill to any blank values
        self._apply_auto_values()
        # Render into HTML every time (Jinja)
        self.rendered_content = self._render_content()  # type: ignore
        # Maintain human-readable status
        self._sync_status()

    def before_submit(self):
        # Signature must exist at submit time
        if not getattr(self, "signature", None):
            frappe.throw("Signature is required before submitting the Consent Form.")
        # Timestamp and status on submit
        if not getattr(self, "signed_on", None):
            self.signed_on = now_datetime()  # type: ignore
        self.status = "Signed"  # type: ignore

    def on_submit(self):
        # Safety: lock critical fields post-submit (Customer, Template)
        self._lock_when_submitted()

    def on_cancel(self):
        # Keep status aligned
        self.status = "Cancelled"  # type: ignore

    # Helpers --------------------------------------------------------------

    def _get_template(self) -> Document:
        if not self.consent_template:
            frappe.throw("Consent Template is required.")
        return frappe.get_doc("Consent Template", self.consent_template)  # type: ignore

    def _ensure_required_fields(self) -> None:
        """Ensure each template required field exists in child table."""
        tmpl = self._get_template()
        existing = {frappe.scrub(r.field_label): r for r in (self.consent_field_values or [])}  # type: ignore
        changed = False
        for req in (tmpl.required_fields or []):  # type: ignore
            key = frappe.scrub(req.field_label or "")
            if key and key not in existing:
                row = self.append("consent_field_values", {})  # type: ignore
                row.field_label = req.field_label
                row.field_type = req.field_type
                row.field_value = req.default_value or ""
                changed = True
        if changed:
            # child append marks the doc dirty automatically
            ...

    def _apply_auto_values(self) -> None:
        """
        Fill blank child values using:
        1) Template defaults
        2) Consent Settings mapping (Single) — variable_name -> source doc field
        Mapping row semantics:
            - enabled (Check)
            - variable_name (snake_case; e.g., customer_name)
            - source_doctype (e.g., Customer)
            - form_link_field (e.g., customer)  # link field on this Consent Form
            - source_fieldname (e.g., customer_name)
            - default_value (fallback)
        """
        tmpl = self._get_template()

        # 1) Template defaults (by original label)
        t_defaults: Dict[str, str] = {}
        for req in (tmpl.required_fields or []):  # type: ignore
            lbl = (req.field_label or "").strip()
            if lbl:
                t_defaults[lbl] = req.default_value or ""

        # 2) Settings-driven fetches (by variable_name)
        settings = _get_settings()
        var_values: Dict[str, Any] = {}
        if settings and getattr(settings, "enable_auto_fill", 0):
            for m in (settings.mappings or []):
                if not getattr(m, "enabled", 0):
                    continue
                var = (m.variable_name or "").strip()
                if not var:
                    continue
                fetched = None
                # Prefer source_doctype via link field, if configured
                if m.source_doctype and m.form_link_field and m.source_fieldname:
                    link_name = getattr(self, m.form_link_field, None)
                    if link_name:
                        fetched = frappe.db.get_value(m.source_doctype, link_name, m.source_fieldname)
                # Fallback to mapping default_value
                if fetched is None and m.default_value:
                    fetched = m.default_value
                if fetched is not None:
                    var_values[var] = fetched

        # Apply to child table rows if blank
        for row in (self.consent_field_values or []):  # type: ignore
            if row.field_value:
                continue
            # A) settings mapping keyed by scrub(label) -> variable_name
            scrub = frappe.scrub(row.field_label or "")
            if scrub in var_values:
                row.field_value = var_values[scrub]
                continue
            # B) template default by original label
            if (row.field_label or "") in t_defaults and t_defaults[row.field_label]:
                row.field_value = t_defaults[row.field_label]

    def _jinja_context(self) -> Dict[str, Any]:
        """
        Build Jinja context:
        - date (YYYY-MM-DD)
        - doc (the Consent Form itself, as 'form')
        - child values as snake_case keys from their labels
        - also include settings-derived variables (by variable_name)
        """
        ctx: Dict[str, Any] = {
            "date": nowdate(),
            "form": self,
        }

        # Child values
        for row in (self.consent_field_values or []):  # type: ignore
            key = frappe.scrub(row.field_label or "")
            if key:
                ctx[key] = row.field_value or ""

        # Settings variables (variable_name) override or extend
        settings = _get_settings()
        if settings and getattr(settings, "enable_auto_fill", 0):
            for m in (settings.mappings or []):
                if not getattr(m, "enabled", 0):
                    continue
                var = (m.variable_name or "").strip()
                if not var:
                    continue
                # Resolve value in the same fashion as _apply_auto_values
                value = None
                if m.source_doctype and m.form_link_field and m.source_fieldname:
                    link_name = getattr(self, m.form_link_field, None)
                    if link_name:
                        value = frappe.db.get_value(m.source_doctype, link_name, m.source_fieldname)
                if value is None and m.default_value:
                    value = m.default_value
                if value is not None:
                    ctx[var] = value

        return ctx

    def _render_content(self) -> str:
        """Render template content using Frappe Jinja environment."""
        tmpl = self._get_template()
        raw = tmpl.content or ""  # type: ignore
        # Use Frappe's pre-configured Jinja environment (respects filters & sandbox)
        jenv = frappe.get_jenv()
        try:
            template = jenv.from_string(raw)
            html = template.render(self._jinja_context())
        except Exception as e:
            frappe.throw(f"Template rendering failed: {frappe.as_unicode(e)}")
        return html

    def _sync_status(self) -> None:
        """Keep 'status' human-friendly based on docstatus/signature."""
        if self.docstatus == 2:
            self.status = "Cancelled"  # type: ignore
        elif self.docstatus == 1:
            self.status = "Signed"  # type: ignore
        else:
            # Draft states
            self.status = "Draft"  # type: ignore

    def _lock_when_submitted(self) -> None:
        """Block changes to Customer/Consent Template post-submit."""
        changed = self.get_dirty_fields() or {}
        blocked = {"customer", "consent_template"}
        if any(k in changed for k in blocked):
            frappe.throw("Cannot modify Customer or Consent Template after submission.")

# Public API ---------------------------------------------------------------

@frappe.whitelist()
def render_preview(name: str) -> str:
    """Return rendered HTML without saving (for Preview)."""
    doc = frappe.get_doc("Consent Form", name)
    return doc._render_content()
