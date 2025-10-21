from __future__ import annotations

import frappe
from frappe.model.document import Document


class InstrumentsOwned(Document):
    """Child table storing ownership metadata for player instruments."""

    def validate(self) -> None:  # pragma: no cover - minimal hook for future hardening
        if self.customer and not frappe.db.exists("Customer", self.customer):
            frappe.throw(frappe._("Customer {0} does not exist").format(self.customer))
        if self.instrument_profile and not frappe.db.exists("Instrument Profile", self.instrument_profile):
            frappe.throw(frappe._("Instrument Profile {0} does not exist").format(self.instrument_profile))
