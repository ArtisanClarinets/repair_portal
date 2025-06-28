# relative path: repair_portal/repair_portal/client_profile/workflow_transition/workflow_transition.py
# updated: 2025-06-27
# version: 1.0.0
# purpose: Controller for Workflow Transition (Client Profile workflows)
# Notes: Standard Frappe child table for workflow transition rules: State + Action → Next State.

import frappe
from frappe.model.document import Document

class WorkflowTransition(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        state: "DF.Link"
        action: "DF.Link"
        next_state: "DF.Link"
        allowed: "DF.Link"
        allow_self_approval: "DF.Check"
        send_email_to_creator: "DF.Check"
        condition: "DF.Code"
        condition_message: "DF.Data"
        parent: "DF.Data"
        parentfield: "DF.Data"
        parenttype: "DF.Data"
        module: "DF.Link"
    # end: auto-generated types
    pass
