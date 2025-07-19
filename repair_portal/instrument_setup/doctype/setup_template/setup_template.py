# File: repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.py
# Updated: 2025-07-18
# Version: 2.0
# Purpose: Setup Template for reusable checklists per clarinet model in service workflows

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class SetupTemplate(Document):
    """
    Represents a reusable setup template for clarinet models. Contains a checklist of items to be completed during the setup process.
    """

    def validate(self) -> None:
        """
        Validates the setup template before saving.
        """
        if not self.checklist_items:
            frappe.throw(_("Checklist items cannot be empty. Please add at least one item."))

        if not self.name:
            frappe.throw(_("Template name is required."))

        if not self.instrument_profile:
            frappe.throw(_("Instrument profile is required for the setup template."))
        if not self.checklist_items:
            frappe.throw(_("Checklist items cannot be empty. Please add at least one item."))

        if not self.workflow_state:
            frappe.throw(_("Workflow state is required for the setup template."))

    def before_save(self) -> None:
        """
        Runs before saving any Setup Template. Validates the checklist items and ensures required fields are set.
        """
        self.validate()

        # Ensure checklist items are unique
        item_names = [item.item_name for item in self.checklist_items]
        if len(item_names) != len(set(item_names)):
            frappe.throw(_("Checklist items must be unique. Please remove duplicates."))

        # Ensure at least one checklist item is completed
        if not any(item.completed for item in self.checklist_items):
            frappe.throw(_("At least one checklist item must be completed."))

    def on_update(self) -> None:
        """
        Runs after the Setup Template is updated. Logs the update for audit purposes.
        """
        frappe.log(f"Setup Template updated: name={self.name}, workflow_state={self.workflow_state}")
        frappe.msgprint(_("Setup Template '{0}' has been updated successfully.").format(self.name))

    def on_trash(self) -> None:
        """
        Runs when the Setup Template is deleted. Logs the deletion for audit purposes.
        """
        frappe.log(f"Setup Template deleted: name={self.name}, workflow_state={self.workflow_state}")
        frappe.msgprint(_("Setup Template '{0}' has been deleted successfully.").format(self.name))
        # Optionally, you can add logic to handle related documents or cleanup
        if frappe.db.exists("Clarinet Initial Setup", {"setup_template": self.name}):
            frappe.throw(
                _(
                    "Cannot delete Setup Template '{0}' as it is linked to existing Clarinet Initial Setups."
                ).format(self.name)
            )
        # Optionally, you can add logic to handle related documents or cleanup
        if frappe.db.exists("Setup Checklist Item", {"parent": self.name}):
            frappe.db.delete("Setup Checklist Item", {"parent": self.name})
            frappe.msgprint(
                _("Checklist items for Setup Template '{0}' have been deleted.").format(self.name)
            )
        # Optionally, you can add logic to handle related documents or cleanup
        if frappe.db.exists("Instrument Profile", {"setup_template": self.name}):
            frappe.db.set_value("Instrument Profile", {"setup_template": self.name}, "setup_template", "")
            frappe.msgprint(
                _("Setup Template '{0}' has been removed from related Instrument Profiles.").format(self.name)
            )

    def on_load(self) -> None:
        """
        Runs when the Setup Template is loaded. Can be used to initialize or fetch related data.
        """
        if not self.checklist_items:
            self.checklist_items = frappe.get_all(
                "Setup Checklist Item", filters={"parent": self.name}, fields=["*"]
            )
            frappe.msgprint(_("Checklist items for Setup Template '{0}' have been loaded.").format(self.name))
        if not self.instrument_profile:
            self.instrument_profile = frappe.get_value(
                "Instrument Profile", {"setup_template": self.name}, "name"
            )
            if self.instrument_profile:
                frappe.msgprint(
                    _("Instrument Profile '{0}' has been linked to Setup Template '{1}'.").format(
                        self.instrument_profile, self.name
                    )
                )
            else:
                frappe.msgprint(_("No Instrument Profile is linked to this Setup Template."))
        if not self.workflow_state:
            self.workflow_state = "Draft"
            frappe.msgprint(
                _("Workflow state for Setup Template '{0}' has been set to Draft.").format(self.name)
            )
        frappe.log(f"Setup Template loaded: name={self.name}, workflow_state={self.workflow_state}")
        frappe.msgprint(_("Setup Template '{0}' has been loaded successfully.").format(self.name))
        if frappe.db.exists("Setup Checklist Item", {"parent": self.name}):
            frappe.msgprint(_("Checklist items for Setup Template '{0}' have been loaded.").format(self.name))
        else:
            frappe.msgprint(_("No checklist items found for Setup Template '{0}'.").format(self.name))
        if frappe.db.exists("Instrument Profile", {"setup_template": self.name}):
            frappe.msgprint(
                _("Instrument Profile '{0}' is linked to Setup Template '{1}'.").format(
                    self.instrument_profile, self.name
                )
            )
        else:
            frappe.msgprint(_("No Instrument Profile is linked to this Setup Template."))
