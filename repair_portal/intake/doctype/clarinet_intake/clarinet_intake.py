# Relative Path: repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py
# Last Updated: 2025-07-04
# Version: v4.1
# Purpose: Clarinet Intake lifecycle with auto Instrument Profile and Quality Inspection creation
# Dependencies: Frappe Framework >= v15

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
import frappe.utils

from . import clarinet_intake_block_flagged

# ---------------------------------------------------------------------------
# Workflow helpers
# ---------------------------------------------------------------------------

workflow = frappe.get_doc("Workflow", "Clarinet Intake Workflow")
# rows are WorkflowDocumentState objects in Frappe ≥ v15
states = workflow.states or []
valid_states = {row.state for row in states}


class ClarinetIntake(Document):
    """
    Clarinet Intake Controller
    Handles validation, lifecycle hooks, and automatic related record creation.
    """

    # ---------------------------------------------------------------------
    # Core validations
    # ---------------------------------------------------------------------

    def validate(self) -> None:
        """Run on every save."""
        clarinet_intake_block_flagged.before_save(self)
        self._ensure_instrument_profile()
        if self.intake_type == "Inventory":
            self._ensure_quality_inspection()

    def before_insert(self) -> None:
        self._check_write_permissions()

    def before_submit(self) -> None:
        if self.intake_type == "Inventory" and not self.checklist:
            frappe.throw(
                _("QC Checklist must be completed before submitting this Intake.")
            )
        self._check_submit_permissions()

    def before_cancel(self) -> None:
        self._check_cancel_permissions()

    # ---------------------------------------------------------------------
    # Workflow-state validation
    # ---------------------------------------------------------------------

    def _validate_workflow_state(self) -> None:
        """Ensure ``self.workflow_state`` is one of the states defined in the Workflow."""
        if not states:
            frappe.throw(_("Workflow states not found"))

        if self.workflow_state and self.workflow_state not in valid_states:
            frappe.throw(
                _("Invalid workflow state: {0}").format(self.workflow_state)
            )

        # If blank, initialise with the first state from the Workflow
        if not self.workflow_state and states:
            self.workflow_state = states[0].state  # attribute access, not dict subscript

    # ---------------------------------------------------------------------
    # Permission checks
    # ---------------------------------------------------------------------

    def _check_write_permissions(self) -> None:
        if not frappe.has_permission(self.doctype, "write"):
            frappe.throw(_("You do not have permission to save this Intake."))

    def _check_submit_permissions(self) -> None:
        if not frappe.has_permission(self.doctype, "submit"):
            frappe.throw(_("You do not have permission to submit this Intake."))

    def _check_cancel_permissions(self) -> None:
        if not frappe.has_permission(self.doctype, "cancel"):
            frappe.throw(_("You do not have permission to cancel this Intake."))

    # ---------------------------------------------------------------------
    # Utility helpers
    # ---------------------------------------------------------------------

    def _ensure_instrument_profile(self) -> None:
        """Create or link an Instrument Profile record."""
        # … existing implementation …

    def _ensure_quality_inspection(self) -> None:
        """Create a Quality Inspection for 'Inventory' intakes."""
        # … existing implementation …

    def _log_transition(self, action: str) -> None:
        self.add_comment(
            "Comment",
            _("Workflow action '{0}' performed by {1}").format(
                action, frappe.session.user
            ),
        )
        frappe.publish_realtime(
            "clarinet_intake_workflow_action",
            {
                "intake_name": self.name,
                "action": action,
                "user": frappe.session.user,
            },
            user=frappe.session.user,
        )