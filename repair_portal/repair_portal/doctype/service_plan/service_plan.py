# Path: repair_portal/repair_portal/doctype/service_plan/service_plan.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Service Plan - manages service planning, scheduling, and customer service agreements.
# Dependencies: frappe, customer management, workflow integration

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class ServicePlan(Document):
    """
    Controller for Service Plan DocType.
    Manages service planning and customer service agreements.
    """

    def validate(self):
        """Validate service plan requirements."""
        if not self.customer:
            frappe.throw(_("Customer is required"))
            
        if not self.plan_name:
            frappe.throw(_("Plan Name is required"))
            
    def before_save(self):
        """Set defaults before saving."""
        if not self.status:
            self.status = "Draft"
            
    def on_submit(self):
        """Actions when service plan is submitted."""
        self.status = "Active"
        
    def on_cancel(self):
        """Actions when service plan is cancelled."""
        self.status = "Cancelled"