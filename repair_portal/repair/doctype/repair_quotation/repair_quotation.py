# /home/frappe/frappe-bench/apps/repair_portal/repair_portal/repair/doctype/repair_quotation/repair_quotation.py
from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime, nowdate

# Correct package path (module = Repair)
from repair_portal.repair.utils import MappingError, create_repair_order_from_quotation


class RepairQuotation(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from repair_portal.repair.doctype.repair_quotation_item.repair_quotation_item import (
            RepairQuotationItem,
        )

        acceptance_source: DF.Literal[Desk, Portal, API]
        accepted_by: DF.Link | None
        accepted_on: DF.Datetime | None
        amended_from: DF.Link | None
        bore_diameter_mm: DF.Float
        brand: DF.Data | None
        company: DF.Link
        condition_notes: DF.SmallText | None
        contact_email: DF.Data | None
        contact_phone: DF.Data | None
        conversion_rate: DF.Float
        currency: DF.Link
        customer_accepted: DF.Check
        customer_name: DF.Link
        customer_primary_contact: DF.Link | None
        discount_amount: DF.Currency
        discount_percent: DF.Float
        discount_type: DF.Literal[Percentage, Amount]
        grand_total: DF.Currency
        instrument_type: DF.Literal[
            "B\u266d Clarinet", "A Clarinet", "E\u266d Clarinet", "C Clarinet", "Bass Clarinet"
        ]
        items: DF.Table[RepairQuotationItem]
        model: DF.Data | None
        owner_signature: DF.Link | None
        quotation_date: DF.Date
        repair_order: DF.Link | None
        rounded_total: DF.Currency
        serial_no: DF.Data | None
        setup_notes: DF.SmallText | None
        status: DF.Literal[Draft, Submitted, Cancelled, Expired, Lost, Accepted]
        subtotal: DF.Currency
        tax_amount: DF.Currency
        tax_rate: DF.Float
        terms: DF.TextEditor | None
        title: DF.Data
        total_labor: DF.Currency
        total_parts: DF.Currency
        valid_till: DF.Date | None
    # end: auto-generated types
    """Clarinet Repair Quotation (parent) – auto-computes totals and can
    create a linked Repair Order upon acceptance. Idempotent wiring ensures
    repeated clicks won't duplicate orders.
    """

    # ----------------------------
    # Lifecycle
    # ----------------------------
    def before_insert(self):
        if not getattr(self, "owner_signature", None):
            self.owner_signature = frappe.session.user
        if not getattr(self, "quotation_date", None):
            self.quotation_date = nowdate()

    def validate(self):
        self._compute_item_amounts()
        self._compute_totals()
        self._validate_discount()
        self._sync_status_field()

    def on_submit(self):
        # Keep Accepted as-is; otherwise standardize to Submitted
        if self.status in (None, "", "Draft", "Submitted"):
            self.status = "Submitted"

    def on_cancel(self):
        self.status = "Cancelled"

    # ----------------------------
    # Public API (called from JS/UI)
    # ----------------------------
    @frappe.whitelist()
    def make_repair_order(self, submit_repair_order: int = 0):
        """Manual server action to create a Repair Order (idempotent)."""
        try:
            order = create_repair_order_from_quotation(self, submit=bool(int(submit_repair_order)))
        except MappingError as e:
            frappe.throw(_(str(e)))
        return order.as_dict()

    @frappe.whitelist()
    def accept_and_make_repair_order(self, submit_repair_order: int = 0):
        """Mark as accepted, submit the quotation if needed, then create RO."""
        # Record acceptance metadata immediately
        self._mark_accepted(source="Desk")

        # Acceptance implies finality; submit if still a draft and submittable
        if self.docstatus == 0 and self.meta.is_submittable:  # type: ignore[attr-defined]
            self.submit()

        # Create or reuse the Repair Order (idempotent)
        try:
            order = create_repair_order_from_quotation(self, submit=bool(int(submit_repair_order)))
        except MappingError as e:
            frappe.throw(_(str(e)))

        # Persist linkage on the quotation too (helper also does this if field exists)
        if self.meta.has_field("repair_order"):
            self.db_set("repair_order", order.name)

        return order.as_dict()

    # ----------------------------
    # Internal helpers
    # ----------------------------
    def _mark_accepted(self, source: str = "Desk"):
        """Set acceptance status and stamps if not already accepted."""
        if self.status == "Accepted" and getattr(self, "customer_accepted", 0):
            return

        self.status = "Accepted"
        if self.meta.has_field("customer_accepted"):
            self.customer_accepted = 1
        if self.meta.has_field("accepted_on"):
            self.accepted_on = now_datetime()
        if self.meta.has_field("accepted_by"):
            self.accepted_by = frappe.session.user
        if self.meta.has_field("acceptance_source"):
            self.acceptance_source = source  # type: ignore

    def _compute_item_amounts(self):
        currency_precision = frappe.get_precision(self, "grand_total") or 2  # type: ignore[arg-type]
        for d in self.items or []:  # type: ignore[attr-defined]
            qty = flt(d.qty or 0.0)  # type: ignore
            rate = flt(d.rate or 0.0, currency_precision)  # type: ignore
            d.amount = flt(qty * rate, currency_precision)  # type: ignore

    def _compute_totals(self):
        currency_precision = frappe.get_precision(self, "grand_total") or 2  # type: ignore[arg-type]
        total_labor = 0.0
        total_parts = 0.0

        for d in self.items or []:  # type: ignore[attr-defined]
            if (d.item_type or "").lower() == "labor" or flt(d.hours) > 0:  # type: ignore
                total_labor += flt(d.amount)  # type: ignore
            else:
                total_parts += flt(d.amount)  # type: ignore

        self.total_labor = flt(total_labor, currency_precision)
        self.total_parts = flt(total_parts, currency_precision)
        subtotal = self.total_labor + self.total_parts
        self.subtotal = flt(subtotal, currency_precision)

        # Discount
        discount_amt = 0.0
        if (self.discount_type or "Amount") == "Amount":  # type: ignore[attr-defined]
            discount_amt = flt(self.discount_amount)
            self.discount_percent = 0.0
        else:
            pct = flt(self.discount_percent)
            discount_amt = flt(subtotal * pct / 100.0, currency_precision)
            self.discount_amount = discount_amt

        if discount_amt > subtotal:
            frappe.throw(_("Discount cannot exceed Subtotal."))

        taxable_base = flt(subtotal - discount_amt, currency_precision)

        # Tax
        tax_rate = flt(getattr(self, "tax_rate", 0.0))  # type: ignore[attr-defined]
        self.tax_amount = flt(taxable_base * tax_rate / 100.0, currency_precision)

        # Totals
        self.grand_total = flt(taxable_base + self.tax_amount, currency_precision)
        self.rounded_total = round(self.grand_total)

    def _validate_discount(self):
        if (self.discount_type or "Amount") == "Percentage":  # type: ignore[attr-defined]
            if flt(self.discount_percent) < 0 or flt(self.discount_percent) > 100:
                frappe.throw(_("Discount (%) must be between 0 and 100."))

    def _sync_status_field(self):
        """Keep 'status' coherent with docstatus when not explicitly set."""
        if self.docstatus == 0 and self.status in (None, "", "Submitted"):
            self.status = "Draft"
        elif self.docstatus == 1 and self.status in (None, "", "Draft"):
            self.status = "Submitted"
