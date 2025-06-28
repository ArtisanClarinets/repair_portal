# relative path: repair_portal/repair_portal/client_profile/workflow_action_master/workflow_action_master.py
# updated: 2025-06-27
# version: 1.0.0
# purpose: Controller for Workflow Action Master (Client Profile workflows)
# Notes: Standard Frappe controller. Each record represents an action label for workflow buttons.

import frappe
from frappe.model.document import Document

class WorkflowActionMaster(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        workflow_action_name: "DF.Data"
        module: "DF.Link"
    # end: auto-generated types
    pass
