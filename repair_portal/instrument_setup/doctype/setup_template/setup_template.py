# File: repair_portal/instrument_setup/doctype/setup_template/setup_template.py
# Last Updated: 2025-09-16
# Version: v1.6.1 (minutes-based, deterministic rounding, idempotent recalc)
# Purpose: Robust recomputation of Estimated Hours and Estimated Total Cost.
# Notes:
#   - Primary: Hours = sum(exp_duration_mins) / 60
#   - Fallback (back-compat): if exp_duration_mins <= 0 on a row, use exp_duration_days * hours_per_day
#   - Cost  = (estimated_hours * hourly_rate) + estimated_materials_cost
#   - Hourly rate from Repair Portal Settings.standard_hourly_rate (default 75)
#   - hours_per_day from Repair Portal Settings.hours_per_day (default 8)
#   - Rounding via Decimal(2) ROUND_HALF_UP for stability
# Dependencies: Clarinet Pad Map, Repair Portal Settings

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Any

import frappe
from frappe import _
from frappe.model.document import Document

D2 = Decimal("0.01")  # 2-decimal quantizer
SIXTY = Decimal(60)  # 60 minutes


def _D(x: Any, default: str = "0") -> Decimal:
    """Safe Decimal parser using str() to avoid binary float artifacts."""
    try:
        if x is None or x == "":
            return Decimal(default)
        return Decimal(str(x))
    except Exception:
        return Decimal(default)


def _get_settings_decimal(fieldname: str, default: str) -> Decimal:
    """Fetch a numeric single value from Repair Portal Settings as Decimal."""
    try:
        val = frappe.db.get_single_value("Repair Portal Settings", fieldname)
        return _D(val, default)
    except Exception:
        return Decimal(default)


def _sum_minutes_and_hours(rows) -> tuple[int, Decimal]:
    """
    Sum minutes from child rows; if a row lacks minutes (<=0), fall back to legacy exp_duration_days.
    Returns (total_minutes_int, hours_decimal_quantized_2dp).
    """
    total_minutes = 0
    hours_per_day = _get_settings_decimal("hours_per_day", "8")

    for r in rows or []:
        # Prefer minutes (new field)
        mins = int(_D(getattr(r, "exp_duration_mins", 0)))
        if mins > 0:
            total_minutes += mins
            continue

        # Legacy fallback by *safely* reading a missing field with getattr default
        days = _D(getattr(r, "exp_duration_days", 0))
        if days > 0:
            as_minutes = (days * hours_per_day * SIXTY).to_integral_value(rounding=ROUND_HALF_UP)
            total_minutes += int(as_minutes)
        else:
            # If both mins and days are missing/invalid, count minimum 1 minute to avoid zero-length tasks
            total_minutes += 1

    hours = (Decimal(total_minutes) / SIXTY).quantize(D2, rounding=ROUND_HALF_UP)
    return total_minutes, hours


class SetupTemplate(Document):
    # --------------------- auto-generated types (do not edit) ---------------------
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
        priority: DF.Data  # Select field with priority options
        setup_type: DF.Data  # Select field with setup type options
        template_name: DF.Data
        template_tasks: DF.Table[ClarinetTemplateTask]
    # ------------------------------------------------------------------------------

    def validate(self):
        self.validate_template_consistency()
        self.auto_create_pad_map()
        self.validate_template_tasks()

        # Save path: recompute deterministically and persist
        _, hours = _sum_minutes_and_hours(self.get("template_tasks"))
        self.estimated_hours = float(hours)  # store float; compute with Decimal
        self.estimated_cost = float(self._compute_total_cost(hours))

    # ---------------------------- validations / helpers ---------------------------

    def validate_template_consistency(self):
        if not self.setup_type:
            frappe.throw(_("Setup Type is required for project template."))
        if not self.template_name and self.clarinet_model and self.setup_type:
            self.template_name = f"{self.clarinet_model} - {self.setup_type}"

    def auto_create_pad_map(self):
        if not self.pad_map and self.clarinet_model:
            existing = frappe.db.exists("Clarinet Pad Map", {"clarinet_model": self.clarinet_model})
            if existing:
                self.pad_map = existing  # type: ignore[assignment]
                frappe.msgprint(_("Found existing Pad Map: {0}").format(existing))
            else:
                pad_map = frappe.get_doc(
                    {"doctype": "Clarinet Pad Map", "clarinet_model": self.clarinet_model}
                )
                pad_map.insert(ignore_permissions=True)
                self.pad_map = pad_map.name
                frappe.msgprint(_("Auto-created Pad Map: {0}").format(pad_map.name))

    def validate_template_tasks(self):
        seen = set()
        for row in self.get("template_tasks") or []:
            seq = int(_D(getattr(row, "sequence", 0)))
            if seq in seen:
                frappe.throw(_("Duplicate sequence in Template Tasks: {0}").format(seq))
            seen.add(seq)

            if not getattr(row, "subject", None):
                frappe.throw(_("Template Task subject is required (sequence: {0}).").format(seq))

            # Minutes must be >= 0. We allow 0 to trigger legacy fallback cleanly.
            mins = int(_D(getattr(row, "exp_duration_mins", 0)))
            if mins < 0:
                row.exp_duration_mins = 0

            # Normalize offset (allows negatives for pre-setup planning)
            if getattr(row, "exp_start_offset_days", None) is None:
                row.exp_start_offset_days = 0

    # ------------------------------ computations ---------------------------------

    def _compute_total_cost(self, hours: Decimal) -> Decimal:
        rate = _get_settings_decimal("standard_hourly_rate", "75")
        materials = _D(self.estimated_materials_cost, "0")
        total = (hours * rate + materials).quantize(D2, rounding=ROUND_HALF_UP)
        return total

    # ------------------------------ convenience API -------------------------------

    @frappe.whitelist()
    def recalc(self) -> dict:
        """
        Idempotent compute-only endpoint:
        - Does NOT mutate the document on the server.
        - Returns hours & cost computed from the current child rows + settings.
        """
        _, hours = _sum_minutes_and_hours(self.get("template_tasks"))
        total = self._compute_total_cost(hours)
        return {
            "estimated_hours": float(hours),
            "estimated_cost": float(total),
        }

    @frappe.whitelist()
    def get_template_summary(self):
        return {
            "template_name": self.template_name,
            "setup_type": self.setup_type,
            "estimated_hours": self.estimated_hours,
            "estimated_cost": self.estimated_cost,
            "estimated_materials_cost": self.estimated_materials_cost,
            "default_technician": self.default_technician,
            "priority": self.priority,
            "operations_count": len(self.get("default_operations") or []),
            "checklist_count": len(self.get("checklist_items") or []),
            "tasks_count": len(self.get("template_tasks") or []),
        }
