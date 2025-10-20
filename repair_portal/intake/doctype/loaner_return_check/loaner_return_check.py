# Path: repair_portal/intake/doctype/loaner_return_check/loaner_return_check.py
# Date: 2025-10-01
# Version: 1.1.0
# Description: Server controller for Loaner Return Check; validates condition notes when damage is flagged, ensures data integrity for loaner instrument returns.
# Dependencies: frappe, frappe.model.document

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class LoanerReturnCheck(Document):
    """
    Controller for Loaner Return Check.
    Validates that damage reports include condition notes.
    """

    def validate(self) -> None:
        """Ensure condition notes are provided when damage is flagged."""
        self._validate_damage_documentation()

    def _validate_damage_documentation(self) -> None:
        """Require condition notes when damage is observed."""
        if self.damage_found and not self.condition_notes:  # type: ignore
            frappe.throw(
                _("Please include condition notes when damage is flagged."), title=_("Validation Error")
            )
