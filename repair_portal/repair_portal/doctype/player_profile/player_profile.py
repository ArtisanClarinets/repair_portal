# Path: repair_portal/repair_portal/doctype/player_profile/player_profile.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Player Profile - manages player information and preferences.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class PlayerProfile(Document):
    """Controller for Player Profile documents."""

    def validate(self):
        """Validate player profile requirements."""
        if not self.player_name:
            frappe.throw(_("Player Name is required"))
        if self.email and not frappe.utils.validate_email_address(self.email):
            frappe.throw(_("Invalid email address"))