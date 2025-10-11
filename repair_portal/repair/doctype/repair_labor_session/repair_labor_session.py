"""Child table capturing detailed technician labor sessions per Repair Order."""

from __future__ import annotations

import frappe
from frappe.model.document import Document


class RepairLaborSession(Document):
    """No additional hooks yet; validation handled on parent Repair Order."""

    def before_insert(self):  # pragma: no cover - minimal guard
        if not self.technician:
            self.technician = frappe.session.user
