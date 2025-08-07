# File Relative Path: repair/doctype/default_operations/default_operations.py
# Last Updated: 2025-07-18
# Version: v2.0
# Purpose: Handles default operations for repair processes, including inventory management and maintenance rules.
# Dependencies: frappe, Repair Portal, Inventory Management, Maintenance Rules


from __future__ import annotations

import logging

import frappe
from frappe import _
from frappe.model.document import Document

LOG = frappe.logger("repair_portal.default_operations", allow_site=True)
LOG.setLevel(logging.INFO)


def _err(msg: str, title: str) -> None:
    """Log + create an Error Log entry that is visible in the Desk."""
    LOG.error(msg)
    frappe.log_error(msg, title)


class DefaultOperations(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.instrument_setup.doctype.operation_template.operation_template import OperationTemplate
        from repair_portal.repair_logging.doctype.material_use_log.material_use_log import MaterialUseLog

        material_used: DF.Table[MaterialUseLog]
        operation_template: DF.Table[OperationTemplate]
        operation_type: DF.Literal["", "Inventory", "Maintenance", "Repair"]
    # end: auto-generated types
    """
    Handles default operations for repair processes. This includes inventory management, maintenance rules,
    and other business logic that applies to all repair operations.
    """

    # Define all required attributes with default values
    operation_type: str = ""
    item_code: str = ""
    warehouse: str = ""
    status: str = ""

    def before_save(self) -> None:
        """
        Runs before saving any Default Operations. Validates operation type and applies business rules.
        """
        if self.operation_type not in ["Inventory", "Maintenance", "Repair"]:
            frappe.throw(_("Operation type must be Inventory, Maintenance, or Repair."))

        if self.status == "Blocked":
            _err(f"Edit blocked on operation {self.name}", "Blocked Operation Edit")
            frappe.throw(_("Editing is not allowed while operation is Blocked."))

        if self.operation_type == "Inventory":
            self._handle_inventory_before_save()
        elif self.operation_type == "Maintenance":
            self._handle_maintenance_before_save()
        elif self.operation_type == "Repair":
            self._handle_repair_before_save()
        else:
            frappe.throw(_("Invalid operation type specified."))

    def _handle_inventory_before_save(self) -> None:
        """
        Handles business logic specific to inventory operations before saving.
        """
        # Implement inventory-specific logic here
        pass

    def _handle_maintenance_before_save(self) -> None:
        """
        Handles business logic specific to maintenance operations before saving.
        """
        # Implement maintenance-specific logic here
        pass

    def _handle_repair_before_save(self) -> None:
        """
        Handles business logic specific to repair operations before saving.
        """
        # Implement repair-specific logic here
        pass

    def before_cancel(self) -> None:
        """
        Block cancel if operation is blocked.
        """
        if self.status == "Blocked":
            _err(f"Cancel blocked on operation {self.name}", "Blocked Operation Cancel")
            frappe.throw(_("Canceling a blocked operation is prohibited."))

    def on_trash(self) -> None:
        """
        Custom logic when the document is trashed.
        """
        # Implement any cleanup logic here if necessary
        pass

    def after_insert(self) -> None:
        """
        Custom logic after the document is inserted.
        """
        # Implement any post-insert logic here if necessary
        pass

    def after_save(self) -> None:
        """
        Custom logic after the document is saved.
        """
        # Implement any post-save logic here if necessary
        pass

    def after_rename(self, old_name: str, new_name: str) -> None:
        """
        Custom logic after the document is renamed.
        """
        # Implement any post-rename logic here if necessary
        pass

    def validate(self) -> None:
        """
        Custom validation logic for the document.
        """
        # Implement any additional validation logic here if necessary
        pass

    def on_update(self) -> None:
        """
        Custom logic when the document is updated.
        """
        # Implement any logic here if necessary
        pass

    def onload(self) -> None:
        """
        Custom logic when the document is loaded.
        """
        # Implement any logic here if necessary
        pass

    def get_context(self, context: dict) -> dict:
        """
        Custom context for the document.
        """
        # Implement any context logic here if necessary
        return context

    def get_operations(self) -> list:
        """
        Returns a list of operations associated with this document.
        """
        operations = frappe.get_all("Default Operations", filters={"parent": self.name}, fields=["*"])
        return operations

    def get_operations_for_item(self, item_code: str) -> list:
        """
        Returns a list of operations associated with this document for a specific item.
        """
        operations = frappe.get_all(
            "Default Operations",
            filters={"parent": self.name, "item_code": item_code},
            fields=["*"],
        )
        return operations
