# relative path: repair_portal/repair_portal/client_profile/workflow_document_state/workflow_document_state.py
# updated: 2025-06-27
# version: 1.0.0
# purpose: Controller for Workflow Document State for Client Profile workflows.
# Notes: Standard Frappe controller. Do not modify the auto-generated types section unless extending logic.
#        Maps each Workflow State to a DocStatus for use in the Workflow system.

import frappe
from frappe.model.document import Document

class WorkflowDocumentState(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        workflow_state: "DF.Link"
        doc_status: "DF.Int"
        allow_edit: "DF.Link"  # Optional: add role who can edit at this state
        update_field: "DF.Data"  # Optional
        update_value: "DF.Data"  # Optional
        is_optional_state: "DF.Check"
        avoid_status_override: "DF.Check"
        send_email: "DF.Check"
        next_action_email_template: "DF.Link"
        message: "DF.Data"
        parent: "DF.Data"
        parentfield: "DF.Data"
        parenttype: "DF.Data"
    # end: auto-generated types

    pass  # No additional logic needed unless you want to enforce custom rules

    # begin: auto-generated types
    
    
    # end: auto-generated types