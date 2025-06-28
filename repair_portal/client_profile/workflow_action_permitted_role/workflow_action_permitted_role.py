# relative path: repair_portal/repair_portal/client_profile/workflow_action_permitted_role/workflow_action_permitted_role.py
# updated: 2025-06-27
# version: 1.0.0
# purpose: Controller for Workflow Action Permitted Role (Client Profile workflows)
# Notes: Standard Frappe child table. Whitelists extra roles allowed for each workflow action.

import frappe
from frappe.model.document import Document

class WorkflowActionPermittedRole(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        role: "DF.Link"
        parent: "DF.Data"
        parentfield: "DF.Data"
        parenttype: "DF.Data"
    # end: auto-generated types
    pass
