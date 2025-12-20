# Path: repair_portal/repair_portal/doctype/clarinet_bom_template/clarinet_bom_template.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Clarinet BOM Template - manages bill of materials templates for clarinet repair operations with validation and cost calculations.
# Dependencies: frappe, Item management, repair class templates

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class ClarinetBOMTemplate(Document):
    """
    Controller for Clarinet BOM Template DocType.
    Manages bill of materials templates for clarinet repair operations.
    """

    # ------------------------------------------------------------
    # VALIDATION / SAVE (DRAFT) PHASE
    # ------------------------------------------------------------
    def before_validate(self):
        """Set defaults and normalize data before validation."""
        self._normalize_instrument_model()
        self._validate_naming_series()

    def validate(self):
        """Validate business rules for BOM template."""
        self._validate_instrument_model()
        self._validate_repair_class()
        self._validate_bom_lines()
        self._validate_unique_template()
        self._calculate_totals()

    def before_save(self):
        """Final preparations before saving."""
        self._update_line_sequence()
        self._sync_repair_class_requirements()

    # ------------------------------------------------------------
    # UPDATE PHASE
    # ------------------------------------------------------------
    def on_update(self):
        """Handle template updates and maintain relationships."""
        self._update_related_repair_orders()
        self._refresh_cost_cache()

    # ------------------------------------------------------------
    # PRIVATE HELPER METHODS
    # ------------------------------------------------------------
    def _normalize_instrument_model(self):
        """Normalize instrument model name."""
        if self.instrument_model:
            self.instrument_model = self.instrument_model.strip().title()

    def _validate_naming_series(self):
        """Ensure naming series is set."""
        if not self.naming_series:
            self.naming_series = "CL-BOM-.#####"

    def _validate_instrument_model(self):
        """Validate instrument model is specified."""
        if not self.instrument_model:
            frappe.throw(_("Instrument Model is required"))
            
        if len(self.instrument_model) < 3:
            frappe.throw(_("Instrument Model must be at least 3 characters"))

    def _validate_repair_class(self):
        """Validate repair class exists if specified."""
        if self.repair_class:
            if not frappe.db.exists("Repair Class Template", self.repair_class):
                frappe.throw(_("Repair Class {0} does not exist").format(self.repair_class))

    def _validate_bom_lines(self):
        """Validate BOM lines for consistency and requirements."""
        if not self.lines:
            frappe.msgprint(_("Warning: BOM Template has no lines"), alert=True)
            return
            
        seen_items = set()
        total_lines = len(self.lines)
        
        for idx, line in enumerate(self.lines):
            # Validate required fields
            if not line.item_code:
                frappe.throw(_("Row {0}: Item Code is required").format(idx + 1))
                
            if not line.qty or line.qty <= 0:
                frappe.throw(_("Row {0}: Quantity must be greater than zero").format(idx + 1))
                
            # Check for duplicate items
            if line.item_code in seen_items:
                frappe.throw(_("Row {0}: Duplicate item {1} found").format(idx + 1, line.item_code))
            seen_items.add(line.item_code)
            
            # Validate item exists and is enabled
            item_doc = frappe.get_cached_doc("Item", line.item_code)
            if item_doc.disabled:
                frappe.throw(_("Row {0}: Item {1} is disabled").format(idx + 1, line.item_code))
                
        if total_lines > 50:
            frappe.msgprint(_("Warning: BOM has {0} lines. Consider splitting into multiple templates")
                          .format(total_lines), alert=True)

    def _validate_unique_template(self):
        """Ensure template combination is unique."""
        filters = {
            "instrument_model": self.instrument_model,
            "name": ("!=", self.name)
        }
        
        if self.repair_class:
            filters["repair_class"] = self.repair_class
        else:
            filters["repair_class"] = ("is", "not set")
            
        existing = frappe.db.exists("Clarinet BOM Template", filters)
        if existing:
            frappe.throw(_("BOM Template already exists for this instrument model and repair class"))

    def _calculate_totals(self):
        """Calculate total quantities and estimated costs."""
        if not self.lines:
            return
            
        total_qty = sum(float(line.qty or 0) for line in self.lines)
        total_cost = 0.0
        
        for line in self.lines:
            # Get item cost
            item_rate = frappe.db.get_value("Item Price", {
                "item_code": line.item_code,
                "price_list": frappe.get_cached_value("Buying Settings", None, "buying_price_list")
            }, "price_list_rate") or 0.0
            
            line_cost = float(line.qty or 0) * item_rate
            total_cost += line_cost
            
        # Store calculated values (these would be added as fields in JSON)
        self.total_items = len(self.lines)
        self.total_qty = total_qty
        self.estimated_cost = total_cost

    def _update_line_sequence(self):
        """Update line sequence numbers."""
        for idx, line in enumerate(self.lines):
            line.idx = idx + 1

    def _sync_repair_class_requirements(self):
        """Sync with repair class requirements if applicable."""
        if not self.repair_class:
            return
            
        try:
            repair_class_doc = frappe.get_doc("Repair Class Template", self.repair_class)
            # This would sync required materials from repair class
            frappe.logger().info(f"Syncing BOM template {self.name} with repair class {self.repair_class}")
        except Exception as e:
            frappe.log_error(f"Error syncing repair class: {str(e)}", "BOM Template Sync")

    def _update_related_repair_orders(self):
        """Update any repair orders using this template."""
        if self.has_value_changed("lines"):
            related_order_names = [
                d.name
                for d in frappe.db.get_list(
                    "Repair Order",
                    {"bom_template": self.name, "docstatus": 0},
                    ["name"],
                )
            ]

            if not related_order_names:
                return

            # Performance: Use a single bulk update query to avoid N+1 database calls.
            # This is significantly more efficient than calling `frappe.db.set_value` in a loop.
            ro_doctype = frappe.qb.DocType("Repair Order")
            frappe.qb.update(ro_doctype).set(
                ro_doctype.bom_needs_update, 1
            ).where(
                ro_doctype.name.isin(related_order_names)
            ).run()

            frappe.msgprint(
                _("{0} repair order(s) marked for BOM update").format(
                    len(related_order_names)
                )
            )

    def _refresh_cost_cache(self):
        """Refresh cached cost calculations."""
        cache_key = f"bom_template_cost_{self.name}"
        frappe.cache().delete_value(cache_key)

    # ------------------------------------------------------------
    # PUBLIC API METHODS
    # ------------------------------------------------------------
    @frappe.whitelist()
    def generate_material_request(self, warehouse: str = None, priority: str = "Medium") -> str:
        """Generate material request for all items in this BOM template."""
        if not self.lines:
            frappe.throw(_("No items to request in BOM template"))
            
        # Create Material Request
        mr = frappe.new_doc("Material Request")
        mr.material_request_type = "Purchase"
        mr.priority = priority
        mr.schedule_date = frappe.utils.add_days(frappe.utils.nowdate(), 7)
        
        for line in self.lines:
            mr.append("items", {
                "item_code": line.item_code,
                "description": line.description,
                "qty": line.qty,
                "uom": line.uom,
                "warehouse": warehouse or line.warehouse,
                "schedule_date": mr.schedule_date
            })
            
        mr.insert()
        mr.submit()
        
        frappe.msgprint(_("Material Request {0} created successfully").format(mr.name))
        return mr.name

    @frappe.whitelist()
    def copy_to_new_template(self, new_instrument_model: str, new_repair_class: str = None) -> str:
        """Copy this template to create a new one for different instrument model."""
        # Create new template
        new_template = frappe.copy_doc(self)
        new_template.instrument_model = new_instrument_model
        new_template.repair_class = new_repair_class
        new_template.name = None  # Will be auto-generated
        
        new_template.insert()
        
        frappe.msgprint(_("New BOM Template {0} created").format(new_template.name))
        return new_template.name

    @frappe.whitelist()
    def get_cost_breakdown(self) -> dict:
        """Get detailed cost breakdown for this BOM template."""
        if not self.lines:
            return {"total_cost": 0, "items": []}
            
        cost_breakdown = {"items": [], "total_cost": 0}
        
        for line in self.lines:
            item_rate = frappe.db.get_value("Item Price", {
                "item_code": line.item_code,
                "price_list": frappe.get_cached_value("Buying Settings", None, "buying_price_list")
            }, "price_list_rate") or 0.0
            
            line_cost = float(line.qty or 0) * item_rate
            
            cost_breakdown["items"].append({
                "item_code": line.item_code,
                "description": line.description,
                "qty": line.qty,
                "rate": item_rate,
                "amount": line_cost
            })
            
            cost_breakdown["total_cost"] += line_cost
            
        return cost_breakdown

    def apply_to_repair_order(self, repair_order: str):
        """Apply this BOM template to a repair order."""
        if not frappe.has_permission("Repair Order", "write", repair_order):
            frappe.throw(_("Insufficient permissions to update repair order"))
            
        repair_doc = frappe.get_doc("Repair Order", repair_order)
        
        # Clear existing materials
        repair_doc.planned_materials = []
        
        # Add items from template
        for line in self.lines:
            repair_doc.append("planned_materials", {
                "item": line.item_code,
                "description": line.description,
                "qty": line.qty,
                "uom": line.uom,
                "warehouse": line.warehouse,
                "service_type": line.service_type
            })
            
        repair_doc.bom_template = self.name
        repair_doc.save()
        
        frappe.msgprint(_("BOM Template applied to Repair Order {0}").format(repair_order))