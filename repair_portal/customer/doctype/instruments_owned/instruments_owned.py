# Path: repair_portal/repair_portal/customer/doctype/instruments_owned/instruments_owned.py
# Date: 2025-01-27
# Version: 3.0.0
# Description: Child table for tracking customer-owned instruments with validation and sync capabilities
# Dependencies: frappe.model.document, Customer, Serial No, Instrument Profile

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now


class InstrumentsOwned(Document):
    """
    Child table for tracking instruments owned by customers.
    
    Manages customer-instrument relationships with validation,
    ownership tracking, and automatic synchronization with instrument profiles.
    """
    
    def validate(self) -> None:
        """Validate instrument ownership record"""
        self._validate_required_fields()
        self._validate_instrument_exists()
        self._validate_customer_exists()
        self._validate_ownership_dates()
        self._check_duplicate_ownership()
        self._sync_instrument_details()
    
    def before_save(self) -> None:
        """Pre-save operations"""
        self._update_ownership_status()
        self._set_audit_fields()
    
    def on_update(self) -> None:
        """Post-update operations"""
        self._update_instrument_profile()
        self._log_ownership_change()
    
    def before_delete(self) -> None:
        """Pre-delete operations"""
        self._update_instrument_profile_on_delete()
    
    def _validate_required_fields(self) -> None:
        """Validate required fields"""
        if not self.customer:
            frappe.throw(_("Customer link is required for Instruments Owned entry"))
        
        if not self.instrument_serial_no and not self.instrument_profile:
            frappe.throw(_("Either Instrument Serial No or Instrument Profile is required"))
    
    def _validate_instrument_exists(self) -> None:
        """Validate that the referenced instrument exists"""
        if self.instrument_serial_no:
            if not frappe.db.exists("Serial No", self.instrument_serial_no):
                frappe.throw(_("Instrument Serial No '{0}' does not exist").format(
                    self.instrument_serial_no
                ))
        
        if self.instrument_profile:
            if not frappe.db.exists("Instrument Profile", self.instrument_profile):
                frappe.throw(_("Instrument Profile '{0}' does not exist").format(
                    self.instrument_profile
                ))
    
    def _validate_customer_exists(self) -> None:
        """Validate that the customer exists"""
        if not frappe.db.exists("Customer", self.customer):
            frappe.throw(_("Customer '{0}' does not exist").format(self.customer))
    
    def _validate_ownership_dates(self) -> None:
        """Validate ownership date logic"""
        if self.purchased_date and self.sold_date and self.sold_date < self.purchased_date:
            frappe.throw(_("Sold date cannot be earlier than purchased date"))
        
        if self.warranty_end_date and self.purchased_date:
            if self.warranty_end_date < self.purchased_date:
                frappe.throw(_("Warranty end date cannot be earlier than purchased date"))
    
    def _check_duplicate_ownership(self) -> None:
        """Check for duplicate ownership records"""
        filters = {
            "customer": self.customer,
            "name": ["!=", self.name] if not self.is_new() else ["!=", ""]
        }
        
        if self.instrument_serial_no:
            filters["instrument_serial_no"] = self.instrument_serial_no
        
        if self.instrument_profile:
            filters["instrument_profile"] = self.instrument_profile
        
        existing = frappe.db.get_value("Instruments Owned", filters, "name")
        if existing:
            frappe.throw(_("Duplicate ownership record found: {0}").format(existing))
    
    def _sync_instrument_details(self) -> None:
        """Sync instrument details from linked records"""
        if self.instrument_serial_no and not self.instrument_name:
            # Get instrument details from Serial No
            serial_details = frappe.db.get_value("Serial No", 
                self.instrument_serial_no,
                ["item_code", "item_name"]
            )
            if serial_details:
                self.instrument_name = serial_details[1] or serial_details[0]
        
        if self.instrument_profile and not self.instrument_name:
            # Get instrument details from Instrument Profile
            profile_details = frappe.db.get_value("Instrument Profile", 
                self.instrument_profile,
                ["instrument_name", "brand", "model"]
            )
            if profile_details:
                self.instrument_name = profile_details[0]
                if not self.brand and profile_details[1]:
                    self.brand = profile_details[1]
                if not self.model and profile_details[2]:
                    self.model = profile_details[2]
    
    def _update_ownership_status(self) -> None:
        """Update ownership status based on dates"""
        current_date = frappe.utils.getdate()
        
        if self.sold_date and self.sold_date <= current_date:
            self.ownership_status = "Sold"
        elif self.purchased_date and self.purchased_date <= current_date:
            self.ownership_status = "Owned"
        else:
            self.ownership_status = "Pending"
    
    def _set_audit_fields(self) -> None:
        """Set audit fields"""
        if self.is_new():
            self.created_by = frappe.session.user
            self.created_on = now()
        else:
            self.modified_by = frappe.session.user
            self.modified_on = now()
    
    def _update_instrument_profile(self) -> None:
        """Update linked instrument profile with ownership info"""
        if self.instrument_profile:
            try:
                profile_doc = frappe.get_doc("Instrument Profile", self.instrument_profile)
                profile_doc.current_owner = self.customer
                profile_doc.ownership_status = self.ownership_status
                profile_doc.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Failed to update instrument profile: {str(e)}")
    
    def _update_instrument_profile_on_delete(self) -> None:
        """Clear ownership info from instrument profile when deleting"""
        if self.instrument_profile:
            try:
                profile_doc = frappe.get_doc("Instrument Profile", self.instrument_profile)
                profile_doc.current_owner = ""
                profile_doc.ownership_status = "Available"
                profile_doc.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Failed to clear instrument profile ownership: {str(e)}")
    
    def _log_ownership_change(self) -> None:
        """Log ownership changes for audit trail"""
        if self.has_value_changed("ownership_status"):
            frappe.logger().info(
                f"Instrument ownership changed: {self.instrument_serial_no or self.instrument_profile} "
                f"for customer {self.customer} - Status: {self.ownership_status}"
            )
    
    @frappe.whitelist()
    def get_ownership_history(self) -> list[dict]:
        """Get ownership history for this instrument"""
        filters = {}
        if self.instrument_serial_no:
            filters["instrument_serial_no"] = self.instrument_serial_no
        elif self.instrument_profile:
            filters["instrument_profile"] = self.instrument_profile
        
        return frappe.db.get_list("Instruments Owned",
            filters=filters,
            fields=[
                "name", "customer", "purchased_date", "sold_date", 
                "ownership_status", "warranty_end_date", "created_on"
            ],
            order_by="purchased_date desc"
        )
    
    @frappe.whitelist()
    def check_warranty_status(self) -> dict[str, any]:
        """Check warranty status of the instrument"""
        if not self.warranty_end_date:
            return {"status": "No Warranty", "days_remaining": 0}
        
        current_date = frappe.utils.getdate()
        if self.warranty_end_date >= current_date:
            days_remaining = (self.warranty_end_date - current_date).days
            return {
                "status": "Under Warranty",
                "days_remaining": days_remaining,
                "warranty_end_date": self.warranty_end_date
            }
        else:
            days_expired = (current_date - self.warranty_end_date).days
            return {
                "status": "Warranty Expired",
                "days_expired": days_expired,
                "warranty_end_date": self.warranty_end_date
            }
    
    def get_service_history(self) -> list[dict]:
        """Get service history for this instrument"""
        # This would link to service/repair records
        # Implementation depends on service tracking modules
        return []
