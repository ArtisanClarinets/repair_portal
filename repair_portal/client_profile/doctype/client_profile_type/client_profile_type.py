# ---------------------------------------------------------------------------
# File: repair_portal/client_profile/doctype/client_profile_type/client_profile_type.py
# Version: 1.0.0  •  2025-06-30
#
# Business logic for Client Profile Type master.
# ---------------------------------------------------------------------------

from __future__ import annotations

import frappe
from frappe.model.document import Document


class ClientProfileType(Document):
    # -------------------------------------------------
    # Core hooks
    # -------------------------------------------------
    def validate(self):
        self._deduplicate_default()

    # -------------------------------------------------
    # Internal helpers
    # -------------------------------------------------
    def _deduplicate_default(self):
        """
        Only ONE row may be flagged *Default*.
        If the user ticks ✔ Default on this record,
        automatically untick it on all the others.
        """
        if not self.is_default:
            return

        frappe.db.sql(
            """
            UPDATE `tabClient Profile Type`
               SET is_default = 0
             WHERE name      != %s
        """,
            self.name,
        )
