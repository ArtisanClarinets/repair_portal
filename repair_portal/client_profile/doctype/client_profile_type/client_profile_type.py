# ---------------------------------------------------------------------------
# File: repair_portal/client_profile/doctype/client_profile_type/client_profile_type.py
# Version: 1.1.0  •  2025-07-16
# Purpose: Enforces single-default logic for Client Profile Types
# Dependencies: Frappe ORM, SQL
# ---------------------------------------------------------------------------

from __future__ import annotations

import frappe
from frappe.model.document import Document


class ClientProfileType(Document):
    def validate(self):
        """Ensure only one profile type is marked as default."""
        self._deduplicate_default()

    def _deduplicate_default(self):
        if not self.is_default:
            return

        try:
            frappe.db.sql(
                """
                UPDATE `tabClient Profile Type`
                   SET is_default = 0
                 WHERE name != %s
                """,
                self.name,
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "ClientProfileType: deduplication failed")