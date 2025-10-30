# Path: repair_portal/repair_portal/doctype/repair_order/repair_order.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Repair Order - manages comprehensive repair order workflow.
# Dependencies: frappe

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class RepairOrder(Document):
    """Controller for Repair Order documents."""

    def validate(self):
        """Validate repair order requirements."""
        if not self.get("customer"):
            frappe.throw(_("Customer is required"))
        if not self.get("instrument"):
            frappe.throw(_("Instrument is required"))
        if not self.get("status"):
            frappe.throw(_("Status is required"))

    def before_save(self):
        """Operations before saving the repair order."""
        self.calculate_totals()

    def calculate_totals(self):
        """Calculate total costs for the repair order."""
        total_material_cost = 0
        total_labor_cost = 0
        
        # Calculate material costs
        materials = self.get("materials") or []
        for material in materials:
            cost = material.get("cost") or 0
            total_material_cost += cost
        
        # Calculate labor costs  
        labor_items = self.get("labor_items") or []
        for labor in labor_items:
            cost = labor.get("cost") or 0
            total_labor_cost += cost
        
        self.total_material_cost = total_material_cost
        self.total_labor_cost = total_labor_cost
        self.total_cost = total_material_cost + total_labor_cost

    def on_submit(self):
        """Handle repair order submission."""
        self.update_status("Submitted")
        self.create_linked_documents()

    def on_cancel(self):
        """Handle repair order cancellation."""
        self.update_status("Cancelled")

    def update_status(self, new_status: str):
        """Update repair order status."""
        self.status = new_status
        frappe.logger().info(f"Repair Order {self.name} status updated to {new_status}")

    def create_linked_documents(self):
        """Create linked documents after submission."""
        # Create material requests if needed
        materials = self.get("materials") or []
        if materials:
            self.create_material_requests()
        
        # Create work orders if needed
        self.create_work_orders()

    def create_material_requests(self):
        """Create material requests for required materials."""
        # Implementation for creating material requests
        pass

    def create_work_orders(self):
        """Create work orders for repair tasks."""
        # Implementation for creating work orders
        pass