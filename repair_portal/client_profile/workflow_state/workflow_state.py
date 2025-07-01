# relative path: repair_portal/repair_portal/client_profile/workflow_state/workflow_state.py
# updated: 2025-06-27
# version: 1.0.0
# purpose: Controller for Workflow State (Client Profile workflows)
# Notes: Standard Frappe controller for workflow state objects used in custom app workflows.

from frappe.model.document import Document


class WorkflowState(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        name: "DF.Data"
        style: "DF.Data"
        doc_status: "DF.Int"
        icon: "DF.Data"  # Optional
        module: "DF.Link"
    # end: auto-generated types
    pass
