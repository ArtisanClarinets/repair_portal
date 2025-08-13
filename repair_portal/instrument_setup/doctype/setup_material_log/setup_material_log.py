# Path: repair_portal/repair_portal/instrument_setup/doctype/setup_material_log/setup_material_log.py
# Version: v1.1
# Date: 2025-08-12
# Purpose: Materials used during setup; auto-computes amount

from __future__ import annotations

from frappe.model.document import Document


class SetupMaterialLog(Document):
    def validate(self):
        qty = self.qty or 0
        rate = self.rate or 0
        self.amount = round(qty * rate, 2)
