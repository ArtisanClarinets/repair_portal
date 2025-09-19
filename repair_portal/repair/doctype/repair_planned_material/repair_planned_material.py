# -*- coding: utf-8 -*-
# Relative Path: repair_portal/repair/doctype/repair_planned_material/repair_planned_material.py
# Version: 1.1.0 (2025-09-17)
# Purpose:
#   Child table controller for "Repair Planned Material".
#   - Defensive defaults (UOM from Item.stock_uom -> fallback "Nos")
#   - Normalize numerics (qty, planned_rate)
#   - Compute planned_amount = qty * planned_rate (server-side source of truth)
#
# Notes:
#   Planned materials are estimates used for quoting/planning. Actual usage is
#   mirrored from submitted Stock Entry into "Repair Actual Material".

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class RepairPlannedMaterial(Document):
    def validate(self):
        self._apply_defaults()
        self._normalize_numbers()
        self._compute_amount()

    # ---- helpers -----------------------------------------------------------

    def _apply_defaults(self) -> None:
        # Backfill UOM from Item.stock_uom if blank; fall back to "Nos"
        if not self.uom:
            if self.item_code:
                self.uom = frappe.db.get_value("Item", self.item_code, "stock_uom") or "Nos"
            else:
                self.uom = "Nos"

    def _normalize_numbers(self) -> None:
        # Keep qty non-negative; returns/credits are not expected at the planning stage
        self.qty = max(0.0, flt(self.qty or 0))
        self.planned_rate = flt(self.planned_rate or 0)

    def _compute_amount(self) -> None:
        # planned_amount is read_only in JSON; compute on server for consistency
        self.planned_amount = flt(self.qty) * flt(self.planned_rate)
