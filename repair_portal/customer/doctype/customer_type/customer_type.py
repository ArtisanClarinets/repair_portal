# ---------------------------------------------------------------------------
# File: repair_portal/customer/doctype/customer_type/customer_type.py
# Version: 1.1.0  •  2025-07-16
# Purpose: Enforces single-default logic for Customer Types
# Dependencies: Frappe ORM, SQL
# ---------------------------------------------------------------------------

from __future__ import annotations

import frappe
from frappe.model.document import Document


class CustomerType(Document):
    def validate(self):
        """Ensure only one profile type is marked as default."""
        self._deduplicate_default()

    def _deduplicate_default(self):
        if not self.is_default: # type: ignore
            return

        try:
            frappe.db.sql(
                """
                UPDATE `tabCustomer Type`
                   SET is_default = 0
                 WHERE name != %s
                """,
                self.name, # type: ignore
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "CustomerType: deduplication failed")
