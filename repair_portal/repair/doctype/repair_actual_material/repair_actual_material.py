# Relative Path: repair_portal/repair/doctype/repair_actual_material/repair_actual_material.py
# Version: 1.1.0 (2025-09-17)
# Purpose:
#   Child table controller for "Repair Actual Material".
#   - Defensive defaults (UOM)
#   - Normalize numerics (qty, valuation_rate)
#   - Compute amount = qty * valuation_rate (server-side source of truth)
#
# Notes:
#   "Repair Actual Material" mirrors submitted Stock Entry rows for at-a-glance
#   visibility. Accounting source of truth remains in Stock Ledger / Stock Entry.

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class RepairActualMaterial(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amount: DF.Currency
        description: DF.SmallText | None
        item_code: DF.Link
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        qty: DF.Float
        stock_entry: DF.Link | None
        uom: DF.Link | None
        valuation_rate: DF.Currency
    # end: auto-generated types
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
        # Ensure numbers are clean; negative qty is allowed for returns only—keep non-negative here
        self.qty = max(0.0, flt(self.qty or 0))
        self.valuation_rate = flt(self.valuation_rate or 0)

    def _compute_amount(self) -> None:
        # amount is read_only in JSON; compute on server to keep in sync with mirrors
        self.amount = flt(self.qty) * flt(self.valuation_rate)
