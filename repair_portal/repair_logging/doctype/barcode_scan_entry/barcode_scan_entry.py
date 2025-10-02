# Path: repair_portal/repair_logging/doctype/barcode_scan_entry/barcode_scan_entry.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Barcode scanning with item resolution, security validation, and audit logging for compliance
# Dependencies: frappe, frappe.model.document, frappe.utils

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now


class BarcodeScanEntry(Document):
    """
    Barcode Scan Entry: Log and resolve barcode scans to items with security validation.
    """

    def validate(self):
        """Validate barcode scan data with security and business rules."""
        self._validate_required_fields()
        self._validate_barcode_format()
        self._resolve_barcode_to_item()
        self._validate_scan_permissions()

    def before_insert(self):
        """Set defaults and enforce audit requirements."""
        if not self.scan_time:
            self.scan_time = now()
        
        self._log_barcode_scan_audit()

    def _validate_required_fields(self):
        """Validate all required fields are present."""
        if not self.barcode:
            frappe.throw(_("Barcode is required"))

    def _validate_barcode_format(self):
        """Validate barcode format and length."""
        if len(self.barcode) < 3:
            frappe.throw(_("Barcode must be at least 3 characters long"))
        
        # Prevent potential XSS/injection attempts
        if any(char in self.barcode for char in ['<', '>', '"', "'"]):
            frappe.throw(_("Barcode contains invalid characters"))

    def _resolve_barcode_to_item(self):
        """Attempt to resolve barcode to an item."""
        if not self.linked_item:
            # Try to find item by barcode
            item_code = frappe.db.get_value('Item Barcode', 
                {'barcode': self.barcode}, 'parent')
            
            if item_code:
                # Validate item is active
                item_data = frappe.db.get_value('Item', item_code, 
                    ['disabled', 'item_name'])
                
                if item_data and not item_data[0]:  # not disabled
                    self.linked_item = item_code
                    frappe.msgprint(_("Barcode resolved to item: {0}").format(item_data[1]))
                else:
                    frappe.msgprint(_("Barcode matches disabled item: {0}").format(item_code))
            else:
                # Try direct item code match
                if frappe.db.exists('Item', self.barcode):
                    item_data = frappe.db.get_value('Item', self.barcode, 
                        ['disabled', 'item_name'])
                    if item_data and not item_data[0]:
                        self.linked_item = self.barcode
                        frappe.msgprint(_("Barcode matched item code: {0}").format(item_data[1]))

    def _validate_scan_permissions(self):
        """Validate user permissions for scanning operations."""
        if not frappe.has_permission("Item", "read"):
            frappe.throw(_("You do not have permission to scan items"))

    def _log_barcode_scan_audit(self):
        """Log barcode scan for audit compliance and security monitoring."""
        frappe.logger("barcode_scan").info({
            "action": "barcode_scanned",
            "barcode": self.barcode,
            "resolved_item": self.linked_item,
            "user": frappe.session.user,
            "timestamp": self.scan_time,
            "context": self.context_note,
            "ip_address": frappe.local.request.environ.get('REMOTE_ADDR') if frappe.local.request else None
        })

    @frappe.whitelist()
    def resolve_barcode(self):
        """
        Whitelisted method to resolve barcode to item.
        Returns item details if found.
        """
        if not self.barcode:
            return {"success": False, "message": "No barcode provided"}

        # Security: Validate user permissions
        if not frappe.has_permission("Item", "read"):
            frappe.throw(_("You do not have permission to resolve items"))

        try:
            self._resolve_barcode_to_item()
            
            if self.linked_item:
                item_details = frappe.db.get_value('Item', self.linked_item, 
                    ['item_name', 'item_group', 'stock_uom'], as_dict=True)
                
                return {
                    "success": True, 
                    "item_code": self.linked_item,
                    "item_details": item_details
                }
            else:
                return {"success": False, "message": "Barcode not found"}
                
        except Exception as e:
            frappe.log_error(f"Barcode resolution failed: {str(e)}")
            return {"success": False, "message": "Resolution failed"}
