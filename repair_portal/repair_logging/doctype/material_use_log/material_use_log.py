# Path: repair_portal/repair_logging/doctype/material_use_log/material_use_log.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Material usage logging with stock integration, permission enforcement, and audit trail for SOX/ISO compliance
# Dependencies: frappe, frappe.model.document, frappe.permissions

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class MaterialUseLog(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        item_name: DF.Link
        operation_link: DF.DynamicLink | None
        operation_type: DF.Link | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        qty: DF.Float
        remarks: DF.SmallText | None
        source_warehouse: DF.Link | None
        used_on: DF.Data | None

    # end: auto-generated types

    def validate(self):
        """Validate material usage with business rules and data integrity checks."""
        self._validate_required_fields()
        self._validate_item_exists()
        self._validate_warehouse_permissions()
        self._validate_quantity()
        self._validate_operation_link()

    def before_insert(self):
        """Enforce naming conventions and audit requirements."""
        self._log_material_usage_audit()

    def on_submit(self):
        """Create stock movement with proper permission validation."""
        if not frappe.has_permission("Stock Entry", "create"):
            frappe.throw(_("You do not have permission to create Stock Entries"))
        
        self._create_stock_movement()

    def _validate_required_fields(self):
        """Validate all required fields are present."""
        required_fields = ["item_name", "qty"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_item_exists(self):
        """Validate that the referenced item exists and is active."""
        if not frappe.db.exists('Item', self.item_name):
            frappe.throw(_('Item {0} does not exist.').format(self.item_name))
        
        item_data = frappe.db.get_value('Item', self.item_name, ['disabled', 'is_stock_item'])
        if item_data and item_data[0]:  # disabled
            frappe.throw(_('Item {0} is disabled and cannot be used.').format(self.item_name))
        
        if item_data and not item_data[1]:  # not a stock item
            frappe.throw(_('Item {0} is not a stock item.').format(self.item_name))

    def _validate_warehouse_permissions(self):
        """Validate warehouse access permissions."""
        if self.source_warehouse and not frappe.has_permission("Warehouse", "read", self.source_warehouse):
            frappe.throw(_("You do not have permission to access warehouse {0}").format(self.source_warehouse))

    def _validate_quantity(self):
        """Validate quantity is positive and reasonable."""
        if self.qty <= 0:
            frappe.throw(_('Quantity must be greater than zero.'))
        
        # Prevent accidental large quantities (business rule)
        if self.qty > 1000:
            frappe.throw(_('Quantity {0} is unusually large. Please verify.').format(self.qty))

    def _validate_operation_link(self):
        """Validate dynamic link integrity."""
        if self.operation_type and self.operation_link and not frappe.db.exists(self.operation_type, self.operation_link):
            frappe.throw(_('Referenced {0} {1} does not exist.').format(self.operation_type, self.operation_link))

    def _log_material_usage_audit(self):
        """Log material usage for audit compliance."""
        frappe.logger("material_usage").info({
            "action": "material_logged",
            "item": self.item_name,
            "quantity": self.qty,
            "user": frappe.session.user,
            "timestamp": frappe.utils.now(),
            "parent_document": self.parent,
            "source_warehouse": self.source_warehouse
        })

    def _create_stock_movement(self):
        """Create validated stock movement with proper error handling."""
        try:
            # Get item UOM
            item_uom = frappe.db.get_value('Item', self.item_name, 'stock_uom')
            if not item_uom:
                frappe.throw(_('No UOM defined for item {0}').format(self.item_name))

            # Validate stock availability if warehouse specified
            if self.source_warehouse:
                stock_qty = frappe.db.get_value('Bin', 
                    {'item_code': self.item_name, 'warehouse': self.source_warehouse}, 
                    'actual_qty') or 0
                
                if stock_qty < self.qty:
                    frappe.msgprint(_('Warning: Stock ({0}) is less than required quantity ({1}) for item {2}')
                                  .format(stock_qty, self.qty, self.item_name))

            stock_entry = frappe.get_doc({
                'doctype': 'Stock Entry',
                'stock_entry_type': 'Material Issue',
                'posting_date': frappe.utils.today(),
                'items': [{
                    'item_code': self.item_name,
                    'qty': self.qty,
                    'uom': item_uom,
                    's_warehouse': self.source_warehouse,
                    'basic_rate': frappe.db.get_value('Item', self.item_name, 'standard_rate') or 0,
                }],
                'remarks': f'Material used for {self.parenttype} {self.parent}: {self.remarks or ""}'
            })
            
            # Insert with user permissions (no ignore_permissions)
            stock_entry.insert()
            stock_entry.submit()
            
            # Link back to this log
            self.db_set('stock_entry_reference', stock_entry.name)
            
            frappe.logger("material_usage").info({
                "action": "stock_entry_created",
                "stock_entry": stock_entry.name,
                "item": self.item_name,
                "quantity": self.qty,
                "user": frappe.session.user
            })
            
        except Exception as e:
            frappe.log_error(f"Failed to create stock entry for material use log: {str(e)}")
            frappe.throw(_('Failed to create stock movement: {0}').format(str(e)))
