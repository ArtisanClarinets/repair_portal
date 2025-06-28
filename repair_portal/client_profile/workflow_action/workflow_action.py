# relative path: repair_portal/repair_portal/client_profile/workflow_action/workflow_action.py
# updated: 2025-06-27
# version: 1.0.0
# purpose: Controller for Workflow Action (Client Profile workflows)
# Notes: Standard Frappe child table for workflow action instances.

import frappe
from frappe.model.document import Document

class WorkflowAction(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        parent: "DF.Data"
        parentfield: "DF.Data"
        parenttype: "DF.Data"
        workflow_action: "DF.Link"
        reference_doctype: "DF.Link"
        reference_name: "DF.Data"
        status: "DF.Data"
        user: "DF.Link"
        completion_datetime: "DF.Datetime"
    # end: auto-generated types
    pass
