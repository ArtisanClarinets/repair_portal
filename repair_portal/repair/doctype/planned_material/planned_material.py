# Path: repair_portal/repair_portal/doctype/planned_material/planned_material.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Planned Material child table - handles material planning, validation, and inventory integration for repair workflow.
# Dependencies: frappe, erpnext Item/UOM/Warehouse, repair portal settings

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class PlannedMaterial(Document):
    """
    Child table controller for Planned Material records.
    Manages material planning, validation, and inventory integration.
    """

    # ------------------------------------------------------------
    # VALIDATION / SAVE (DRAFT) PHASE
    # ------------------------------------------------------------
    def before_validate(self):
        """Set default values and normalize data before validation."""
        self._set_item_defaults()
        self._normalize_quantities()

    def validate(self):
        """Validate business rules for planned materials."""
        self._validate_item_exists()
        self._validate_quantities()
        self._validate_warehouse_permissions()
        self._validate_vendor_relationship()
        self._validate_lead_time()

    def before_save(self):
        """Final preparations before saving."""
        self._update_description_from_item()
        self._calculate_lead_time()

    # ------------------------------------------------------------
    # PRIVATE HELPER METHODS
    # ------------------------------------------------------------
    def _set_item_defaults(self):
        """Set default UOM and description from Item master."""
        if not self.item:
            return
            
        if not self.uom:
            item_doc = frappe.get_cached_doc("Item", self.item)
            self.uom = item_doc.stock_uom
            
        if not self.qty:
            self.qty = 1.0

    def _normalize_quantities(self):
        """Ensure quantities are positive and properly formatted."""
        if self.qty and self.qty < 0:
            frappe.throw(_("Quantity cannot be negative"))
            
        if self.lead_time_days and self.lead_time_days < 0:
            frappe.throw(_("Lead time cannot be negative"))

    def _validate_item_exists(self):
        """Ensure the item exists and is not disabled."""
        if not self.item:
            return
            
        item_doc = frappe.get_cached_doc("Item", self.item)
        if item_doc.disabled:
            frappe.throw(_("Item {0} is disabled and cannot be planned").format(self.item))

    def _validate_quantities(self):
        """Validate quantity and UOM consistency."""
        if not self.qty or self.qty <= 0:
            frappe.throw(_("Quantity must be greater than zero"))
            
        if self.item and self.uom:
            # Validate UOM exists for this item
            uom_exists = frappe.db.exists("UOM Conversion Detail", {
                "parent": self.item,
                "uom": self.uom
            })
            if not uom_exists and self.uom != frappe.get_cached_value("Item", self.item, "stock_uom"):
                frappe.throw(_("UOM {0} is not valid for item {1}").format(self.uom, self.item))

    def _validate_warehouse_permissions(self):
        """Ensure user has access to the specified warehouse."""
        if not self.warehouse:
            return
            
        if not frappe.has_permission("Warehouse", "read", self.warehouse):
            frappe.throw(_("Insufficient permissions for warehouse {0}").format(self.warehouse))

    def _validate_vendor_relationship(self):
        """Validate vendor exists and is enabled."""
        if not self.vendor:
            return
            
        vendor_doc = frappe.get_cached_doc("Supplier", self.vendor)
        if vendor_doc.disabled:
            frappe.throw(_("Vendor {0} is disabled").format(self.vendor))

    def _validate_lead_time(self):
        """Validate lead time is reasonable."""
        if self.lead_time_days and self.lead_time_days > 365:
            frappe.msgprint(_("Lead time of {0} days seems unusually long").format(self.lead_time_days))

    def _update_description_from_item(self):
        """Auto-populate description from item if empty."""
        if self.item and not self.description:
            self.description = frappe.get_cached_value("Item", self.item, "item_name")

    def _calculate_lead_time(self):
        """Calculate lead time based on vendor and item master data."""
        if self.lead_time_days or not self.vendor or not self.item:
            return
            
        # Try to get lead time from item supplier records
        lead_time = frappe.db.get_value("Item Supplier", {
            "parent": self.item,
            "supplier": self.vendor
        }, "lead_time_days")
        
        if lead_time:
            self.lead_time_days = lead_time

    # ------------------------------------------------------------
    # PUBLIC API METHODS
    # ------------------------------------------------------------
    def get_available_stock(self) -> float:
        """Get current available stock for this item in the specified warehouse."""
        if not self.item or not self.warehouse:
            return 0.0
            
        return frappe.db.get_value("Bin", {
            "item_code": self.item,
            "warehouse": self.warehouse
        }, "actual_qty") or 0.0

    def is_stock_available(self) -> bool:
        """Check if sufficient stock is available."""
        available = self.get_available_stock()
        return available >= (self.qty or 0)

    def get_estimated_cost(self) -> float:
        """Get estimated cost for this planned material."""
        if not self.item or not self.qty:
            return 0.0
            
        # Try to get last purchase rate or valuation rate
        rate = frappe.db.get_value("Item Price", {
            "item_code": self.item,
            "price_list": frappe.get_cached_value("Buying Settings", None, "buying_price_list")
        }, "price_list_rate")
        
        if not rate:
            rate = frappe.get_cached_value("Item", self.item, "valuation_rate") or 0.0
            
        return rate * self.qty

    @frappe.whitelist()
    def create_material_request(self):
        """Create a material request for this planned material."""
        if self.material_request:
            frappe.throw(_("Material Request already exists: {0}").format(self.material_request))
            
        if self.is_stock_available():
            frappe.throw(_("Sufficient stock is available. Material Request not needed."))
            
        # Create Material Request
        mr = frappe.new_doc("Material Request")
        mr.material_request_type = "Purchase"
        mr.schedule_date = frappe.utils.add_days(frappe.utils.nowdate(), self.lead_time_days or 7)
        
        mr.append("items", {
            "item_code": self.item,
            "description": self.description,
            "qty": self.qty,
            "uom": self.uom,
            "warehouse": self.warehouse,
            "schedule_date": mr.schedule_date
        })
        
        mr.insert()
        
        # Update reference
        self.db_set("material_request", mr.name)
        self.db_set("reservation_entry_type", "Material Request")
        self.db_set("reservation_entry", mr.name)
        
        return mr.name