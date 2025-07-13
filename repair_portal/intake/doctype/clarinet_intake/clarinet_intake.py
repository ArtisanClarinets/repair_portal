# --------------------------------------------------------------------------- #
# File Header
#   Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
#   Version: v2.2.0  –  Production (Frappe v15+)
#   Last Updated: 2025-07-13
#   Changelog:
#     • Hardened checklist validation logic (null-safe)
# --------------------------------------------------------------------------- #
from __future__ import annotations
from typing import TYPE_CHECKING, List

import frappe
from frappe import _
from frappe.model.document import Document

from . import clarinet_intake_block_flagged            # (now v2.1)
from repair_portal.intake.utils.emailer import queue_intake_status_email
from repair_portal.logger import get_logger

if TYPE_CHECKING:
    from repair_portal.intake.doctype.clarinet_intake.clarinet_intake import (
        ClarinetIntake,
    )

LOGGER = get_logger(__name__)
ADMIN_USER = "Administrator"      # Fallback if session user is invalid/disabled


# --------------------------------------------------------------------------- #
# Helper
# --------------------------------------------------------------------------- #
def _get_valid_user(user_id: str | None) -> str:
    """Return *user_id* if it is an enabled User; else return Administrator."""
    if user_id and frappe.db.exists("User", {"name": user_id, "enabled": 1}):
        return user_id

    LOGGER.warning(
        "Invalid or disabled owner '%s' supplied — falling back to %s",
        user_id,
        ADMIN_USER,
    )
    return ADMIN_USER


# --------------------------------------------------------------------------- #
# Controller
# --------------------------------------------------------------------------- #
class ClarinetIntake(Document):
    # ------------------------ Early lifecycle ---------------------------- #
    def before_validate(self) -> None:
        """Set a guaranteed-valid owner before Frappe validates the doc."""
        self.owner = _get_valid_user(frappe.session.user)
        LOGGER.info("[OwnerTrace] before_validate → %s", self.owner)

    # --------------------------------------------------------------------- #
    def validate(self) -> None:
        """Business-rule validation and defensive defaults."""
        # Intake-type defaults
        self.intake_type = (self.intake_type or "Inventory").title()

        if self.intake_type == "Inventory":
            self.stock_status = self.stock_status or "Inspection"
            self.repair_status = None
        else:  # Repair
            self.repair_status = self.repair_status or "Pending"
            self.stock_status = None

        # Require customer on Repair intakes
        if self.intake_type == "Repair" and not self.customer:
            frappe.throw(_("Customer is required for Repair intake type."))

        # Checklist completeness
        if self.checklist:
            incomplete: List[str] = [
                (row.accessory or row.item or "<Unnamed>")
                for row in self.checklist
                if getattr(row, "status", None) != "Completed"
            ]
            if incomplete:
                frappe.throw(
                    _("All accessories must be marked completed: {0}")
                    .format(", ".join(incomplete))
                )

        # Flag protections (delegated)
        clarinet_intake_block_flagged.before_save(self)

    # Delegate cancel / trash protections
    before_cancel = clarinet_intake_block_flagged.before_cancel  # type: ignore[attr-defined]
    on_trash      = clarinet_intake_block_flagged.on_trash       # type: ignore[attr-defined]

    # --------------------------- Post-insert ----------------------------- #
    def after_insert(self) -> None:
        """
        Post-creation automation:
          • Queue status e-mail
          • Log creation event
        """
        queue_intake_status_email(self)
        LOGGER.info("New Clarinet Intake %s saved by %s", self.name, self.owner)