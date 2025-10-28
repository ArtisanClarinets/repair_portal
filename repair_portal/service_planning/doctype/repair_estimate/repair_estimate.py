"""Repair Estimate controller with estimator-aware calculations."""

from __future__ import annotations

from typing import Iterable

import frappe
from frappe import _, throw
from frappe.model.document import Document
from frappe.utils import flt


class RepairEstimate(Document):
    """Aggregates line items for clarinet repair planning and portal estimates."""

    def validate(self) -> None:  # noqa: D401
        self._validate_condition_score()
        self._sync_eta_defaults()
        self._compute_line_amounts()

    def _validate_condition_score(self) -> None:
        if self.condition_score is None:
            throw(_("Condition Score is required."))
        if self.condition_score < 0 or self.condition_score > 100:
            throw(_("Condition Score must be between 0 and 100."))

    def _sync_eta_defaults(self) -> None:
        if self.eta_days is None or self.eta_days < 0:
            self.eta_days = 0

    def _compute_line_amounts(self) -> None:
        precision = frappe.get_precision(self, "total_cost") or 2  # type: ignore[arg-type]
        total = 0.0
        for item in self._iter_line_items():
            role = (item.line_role or "").lower()
            qty = flt(getattr(item, "quantity", 0.0))
            hours = flt(getattr(item, "hours", 0.0))
            rate = flt(getattr(item, "rate", 0.0), precision)

            if role == "part":
                if qty <= 0:
                    qty = 1.0
                item.quantity = qty
                item.hours = 0.0
                item.amount = flt(qty * rate, precision)
            else:
                basis = hours or qty
                if basis <= 0:
                    throw(_("Labor or setup lines require hours or quantity."))
                item.hours = basis
                item.quantity = qty or basis
                item.amount = flt(basis * rate, precision)

            total += flt(item.amount, precision)

        self.total_cost = flt(total, precision)

    def _iter_line_items(self) -> Iterable[Document]:
        return tuple(self.get("line_items") or [])  # type: ignore[return-value]
