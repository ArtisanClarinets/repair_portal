# Path: repair_portal/repair_logging/doctype/repair_parts_used/repair_parts_used.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready repair parts tracking with inventory integration, permission enforcement, and compliance logging
# Dependencies: frappe, frappe.model.document, frappe.permissions

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class RepairPartsUsed(Document):
    """
    Repair Parts Used: Track parts consumption during repairs with inventory validation.
    """

    def validate(self):
        """Validate repair parts usage with comprehensive business rules."""
        self._validate_required_fields()
        self._validate_part_exists()
        self._validate_quantity()
        self._validate_warehouse_permissions()
        self._validate_cost_reasonableness()

    def before_insert(self):
        """Set defaults and calculate costs."""
        self._set_default_warehouse()
        self._calculate_part_cost()
        self._log_parts_usage_audit()

    def on_submit(self):
        """Process inventory movement with proper validation."""
        if frappe.db.get_single_value('Repair Settings', 'auto_create_stock_entries'):
            self._create_inventory_movement()

    def _validate_required_fields(self):
        """Validate all required fields are present."""
        required_fields = ["item_code", "qty"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_part_exists(self):
        """Validate that the part exists and is available for use."""
        if not frappe.db.exists('Item', self.item_code):
            frappe.throw(_('Part {0} does not exist in the system.').format(self.item_code))
        
        part_data = frappe.db.get_value('Item', self.item_code, 
            ['disabled', 'is_stock_item', 'item_name', 'maintain_stock'])
        
        if part_data and part_data[0]:  # disabled
            frappe.throw(_('Part {0} is disabled and cannot be used.').format(self.item_code))
        
        if part_data and not part_data[1]:  # not a stock item
            frappe.msgprint(_('Warning: Part {0} is not configured as a stock item.').format(self.item_code))

    def _validate_quantity(self):
        """Validate quantity is positive and within reasonable limits."""
        if flt(self.qty) <= 0:
            frappe.throw(_('Quantity used must be greater than zero.'))
        
        # Business rule: Prevent accidental large quantities
        if flt(self.qty) > 100:
            frappe.throw(_('Quantity {0} is unusually large. Please verify.').format(self.qty))

    def _validate_warehouse_permissions(self):
        """Validate warehouse access and permissions."""
        if self.warehouse:
            if not frappe.has_permission("Warehouse", "read", self.warehouse):
                frappe.throw(_("You do not have permission to access warehouse {0}").format(self.warehouse))
            
            # Validate warehouse exists and is active
            warehouse_data = frappe.db.get_value('Warehouse', self.warehouse, 
                ['disabled', 'is_group'])
            
            if warehouse_data and warehouse_data[0]:  # disabled
                frappe.throw(_('Warehouse {0} is disabled.').format(self.warehouse))
            
            if warehouse_data and warehouse_data[1]:  # is group
                frappe.throw(_('Cannot use group warehouse {0}. Please select a specific warehouse.').format(self.warehouse))

    def _validate_cost_reasonableness(self):
        """Validate cost calculations are reasonable."""
        if self.rate and flt(self.rate) < 0:
            frappe.throw(_('Unit rate cannot be negative.'))
        
        if self.amount and flt(self.amount) < 0:
            frappe.throw(_('Total amount cannot be negative.'))
        
        # Check cost consistency
        if self.rate and self.qty:
            calculated_total = flt(self.rate) * flt(self.qty)
            if self.amount and abs(flt(self.amount) - calculated_total) > 0.01:
                frappe.msgprint(_('Warning: Total amount does not match rate × quantity.'))

    def _set_default_warehouse(self):
        """Set default warehouse from settings if not specified."""
        if not self.warehouse:
            default_warehouse = frappe.db.get_single_value('Repair Settings', 'default_source_warehouse')
            if not default_warehouse:
                default_warehouse = 'Stores - AC'  # Fallback default
            self.warehouse = default_warehouse

    def _calculate_part_cost(self):
        """Calculate part costs based on current rates."""
        if self.item_code and self.qty:
            # Get standard rate or valuation rate
            part_rate = frappe.db.get_value('Item', self.item_code, 'standard_rate')
            
            if not part_rate and self.warehouse:
                # Try to get valuation rate from stock ledger
                part_rate_query = frappe.db.sql("""
                    SELECT AVG(valuation_rate) 
                    FROM `tabStock Ledger Entry` 
                    WHERE item_code = %s AND warehouse = %s 
                    AND valuation_rate > 0
                    ORDER BY posting_date DESC 
                    LIMIT 10
                """, (self.item_code, self.warehouse))
                
                part_rate = part_rate_query[0][0] if part_rate_query and part_rate_query[0][0] else 0
            
            if part_rate:
                self.rate = flt(part_rate)
                self.amount = flt(self.rate) * flt(self.qty)

    def _log_parts_usage_audit(self):
        """Log parts usage for audit compliance."""
        frappe.logger("parts_usage").info({
            "action": "part_consumed",
            "item_code": self.item_code,
            "quantity": self.qty,
            "warehouse": self.warehouse,
            "user": frappe.session.user,
            "timestamp": frappe.utils.now(),
            "parent_document": self.parent,
            "total_amount": self.amount
        })

    def _create_inventory_movement(self):
        """Create stock entry for inventory movement with proper validation."""
        if not frappe.has_permission("Stock Entry", "create"):
            frappe.throw(_("You do not have permission to create Stock Entries"))
        
        try:
            # Check stock availability
            if self.warehouse:
                available_qty = frappe.db.get_value('Bin', 
                    {'item_code': self.item_code, 'warehouse': self.warehouse}, 
                    'actual_qty') or 0
                
                if available_qty < flt(self.qty):
                    frappe.msgprint(_('Warning: Available stock ({0}) is less than required quantity ({1}) for part {2}')
                                  .format(available_qty, self.qty, self.item_code))

            # Get item UOM
            item_uom = frappe.db.get_value('Item', self.item_code, 'stock_uom')
            
            stock_entry = frappe.get_doc({
                'doctype': 'Stock Entry',
                'stock_entry_type': 'Material Issue',
                'purpose': 'Material Issue',
                'posting_date': frappe.utils.today(),
                'company': frappe.defaults.get_global_default("company"),
                'reference_doctype': 'Repair Parts Used',
                'reference_docname': self.name,
                'items': [{
                    'item_code': self.item_code,
                    'qty': flt(self.qty),
                    'uom': item_uom,
                    's_warehouse': self.warehouse,
                    'basic_rate': flt(self.rate) if self.rate else 0,
                    'cost_center': 'Main - AC',
                }],
                'remarks': f'Parts used for repair: {self.parent}'
            })
            
            # Insert with user permissions
            stock_entry.insert()
            stock_entry.submit()
            
            # Link back to this record
            self.db_set('stock_entry', stock_entry.name)
            
            frappe.logger("parts_usage").info({
                "action": "stock_entry_created",
                "stock_entry": stock_entry.name,
                "item_code": self.item_code,
                "quantity": self.qty,
                "user": frappe.session.user
            })
            
            frappe.msgprint(f'Stock Entry {stock_entry.name} created for part usage')
            
        except Exception as e:
            frappe.log_error(f"Failed to create stock entry for repair parts: {str(e)}")
            frappe.throw(_('Failed to create inventory movement: {0}').format(str(e)))

    def validate_inventory_availability(self):
        """Check if sufficient inventory is available - deprecated method for compatibility."""
        if self.item_code and self.warehouse:
            available_qty = frappe.db.get_value('Bin', 
                {'item_code': self.item_code, 'warehouse': self.warehouse}, 
                'actual_qty') or 0
            
            if flt(self.qty) > flt(available_qty):
                frappe.msgprint(
                    f'Warning: Requested quantity ({self.qty}) exceeds available stock ({available_qty}) for {self.item_name or self.item_code}',
                    alert=True,
                )
