# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/doctype/clarinet_intake_settings/clarinet_intake_settings.py
# Last Updated: 2025-10-11
# Version: v1.3
# Purpose:
#   Backend controller for Clarinet Intake Settings (Single DocType).
#   • Validates default links used across intake automation flows.
#   • Enforces consent template integrity and SLA fallbacks.
#   • Provides a helper for callers to fetch settings with safe defaults.

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document

DEFAULT_SLA_TARGET_HOURS = 72
DEFAULT_SLA_LABEL = "Promise by"


class ClarinetIntakeSettings(Document):
    """Settings DocType controller for intake automation."""

    def validate(self) -> None:
        """Ensure referenced records exist and defaults remain sane."""

        self._validate_link("default_item_group", "Item Group", fallback="Clarinets")
        self._validate_link("default_inspection_warehouse", "Warehouse")
        self._validate_link("buying_price_list", "Price List", fallback="Standard Buying")
        self._validate_link("selling_price_list", "Price List", fallback="Standard Selling")
        self._validate_link("stock_uom", "UOM", fallback="Nos")
        self._validate_consent_template()
        self._ensure_naming_hint()
        self._ensure_sla_defaults()

    def _validate_link(self, fieldname: str, doctype: str, *, fallback: str | None = None) -> None:
        value = (getattr(self, fieldname, None) or "").strip()  # type: ignore[attr-defined]
        if not value:
            if fallback and frappe.db.exists(doctype, fallback):
                setattr(self, fieldname, fallback)
            return

        if frappe.db.exists(doctype, value):
            return

        if fallback and frappe.db.exists(doctype, fallback):
            setattr(self, fieldname, fallback)
            return

        frappe.msgprint(
            _("{doctype} '{value}' not found. Clearing the value.").format(
                doctype=doctype, value=frappe.as_unicode(value)
            ),
            indicator="orange",
        )
        setattr(self, fieldname, None)

    def _validate_consent_template(self) -> None:
        if not self.auto_create_consent_form:  # type: ignore[attr-defined]
            return
        template = getattr(self, "default_consent_template", None)
        if template and not frappe.db.exists("Consent Template", template):
            frappe.msgprint(
                _("Consent Template '{0}' not found. Please select a valid template.").format(template),
                indicator="orange",
            )
            self.default_consent_template = None  # type: ignore[attr-defined]

    def _ensure_naming_hint(self) -> None:
        if self.intake_naming_series or self.intake_id_pattern:  # type: ignore[attr-defined]
            return
        self.intake_id_pattern = "CI-.{YYYY}.-.#####"  # type: ignore[attr-defined]

    def _ensure_sla_defaults(self) -> None:
        if not self.sla_target_hours:  # type: ignore[attr-defined]
            self.sla_target_hours = DEFAULT_SLA_TARGET_HOURS  # type: ignore[attr-defined]
        if not self.sla_label:  # type: ignore[attr-defined]
            self.sla_label = DEFAULT_SLA_LABEL  # type: ignore[attr-defined]


def get_intake_settings() -> dict:
    """Return Clarinet Intake Settings as a dict with sensible fallbacks."""

    doc = frappe.get_single("Clarinet Intake Settings")
    data = doc.as_dict()

    if not data.get("default_item_group") and frappe.db.exists("Item Group", "Clarinets"):
        data["default_item_group"] = "Clarinets"
    if not data.get("stock_uom") and frappe.db.exists("UOM", "Nos"):
        data["stock_uom"] = "Nos"

    if not data.get("intake_naming_series") and not data.get("intake_id_pattern"):
        data["intake_id_pattern"] = "CI-.{YYYY}.-.#####"

    data.setdefault("sla_target_hours", DEFAULT_SLA_TARGET_HOURS)
    data.setdefault("sla_label", DEFAULT_SLA_LABEL)

    return data
