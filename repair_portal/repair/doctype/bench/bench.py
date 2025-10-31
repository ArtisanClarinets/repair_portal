# Path: repair_portal/repair_portal/doctype/bench/bench.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Bench - manages repair workstation/bench setup, technician assignments, and capacity tracking.
# Dependencies: frappe, User doctype, repair portal settings

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class Bench(Document):
    """
    Controller for Bench DocType.
    Manages repair workstations, technician assignments, and capacity tracking.
    """

    # ------------------------------------------------------------
    # NAMING PHASE
    # ------------------------------------------------------------
    def autoname(self):
        """Auto-generate bench name if not specified."""
        if not self.name and self.location:
            # Generate name like "Bench-MainFloor-001"
            existing_count = frappe.db.count("Bench", filters={"location": self.location})
            self.name = f"Bench-{self.location.replace(' ', '')}-{existing_count + 1:03d}"

    # ------------------------------------------------------------
    # VALIDATION / SAVE (DRAFT) PHASE
    # ------------------------------------------------------------
    def before_validate(self):
        """Set defaults and normalize data before validation."""
        self._normalize_location()
        self._set_default_values()

    def validate(self):
        """Validate business rules for bench configuration."""
        self._validate_location_required()
        self._validate_technician_permissions()
        self._validate_unique_location_name()
        self._validate_technician_availability()

    def before_save(self):
        """Final preparations before saving."""
        self._update_technician_bench_assignment()

    # ------------------------------------------------------------
    # UPDATE PHASE
    # ------------------------------------------------------------
    def on_update(self):
        """Handle bench updates and maintain relationships."""
        self._sync_technician_assignments()
        self._update_capacity_cache()

    # ------------------------------------------------------------
    # DELETE (TRASH)
    # ------------------------------------------------------------
    def on_trash(self):
        """Cleanup before deletion."""
        self._validate_no_active_repairs()
        self._cleanup_technician_assignments()

    # ------------------------------------------------------------
    # PRIVATE HELPER METHODS
    # ------------------------------------------------------------
    def _normalize_location(self):
        """Normalize location field."""
        if self.location:
            self.location = self.location.strip().title()

    def _set_default_values(self):
        """Set any default values if not provided."""
        if not self.location:
            self.location = "Main Floor"

    def _validate_location_required(self):
        """Ensure location is specified."""
        if not self.location or not self.location.strip():
            frappe.throw(_("Location is required for bench setup"))

    def _validate_technician_permissions(self):
        """Validate the default technician exists and has proper permissions."""
        if not self.default_technician:
            return
            
        # Check if user exists and is enabled
        user_doc = frappe.get_cached_doc("User", self.default_technician)
        if user_doc.enabled == 0:
            frappe.throw(_("Technician {0} is disabled").format(self.default_technician))
            
        # Check if user has technician role
        user_roles = frappe.get_roles(self.default_technician)
        if "Repair Technician" not in user_roles:
            frappe.throw(_("User {0} does not have Repair Technician role").format(self.default_technician))

    def _validate_unique_location_name(self):
        """Ensure location names are unique within the same area."""
        if self.is_new():
            existing = frappe.db.exists("Bench", {
                "location": self.location,
                "name": ("!=", self.name)
            })
            if existing:
                frappe.throw(_("A bench already exists at location: {0}").format(self.location))

    def _validate_technician_availability(self):
        """Check if technician is already assigned to another bench."""
        if not self.default_technician:
            return
            
        existing_bench = frappe.db.get_value("Bench", {
            "default_technician": self.default_technician,
            "name": ("!=", self.name)
        }, "name")
        
        if existing_bench:
            frappe.msgprint(_("Warning: Technician {0} is already assigned to bench {1}")
                          .format(self.default_technician, existing_bench), 
                          alert=True)

    def _update_technician_bench_assignment(self):
        """Update technician's bench assignment in their profile."""
        if self.default_technician:
            # Update technician's current bench reference
            technician_doc = frappe.db.exists("Technician", {"user": self.default_technician})
            if technician_doc:
                frappe.db.set_value("Technician", technician_doc, "current_bench", self.name)

    def _sync_technician_assignments(self):
        """Sync technician assignments when bench is updated."""
        if self.has_value_changed("default_technician"):
            # Clear old assignment
            old_technician = self.get_db_value("default_technician")
            if old_technician:
                old_tech_doc = frappe.db.exists("Technician", {"user": old_technician})
                if old_tech_doc:
                    frappe.db.set_value("Technician", old_tech_doc, "current_bench", None)
            
            # Set new assignment
            if self.default_technician:
                self._update_technician_bench_assignment()

    def _update_capacity_cache(self):
        """Update cached capacity calculations."""
        # This would integrate with repair scheduling system
        # Clear any cached capacity calculations
        frappe.cache().delete_value(f"bench_capacity_{self.name}")

    def _validate_no_active_repairs(self):
        """Ensure no active repairs are assigned to this bench."""
        active_repairs = frappe.db.count("Repair Order", {
            "bench": self.name,
            "docstatus": 1,
            "status": ("not in", ["Completed", "Cancelled"])
        })
        
        if active_repairs > 0:
            frappe.throw(_("Cannot delete bench {0}: {1} active repair(s) are assigned")
                        .format(self.name, active_repairs))

    def _cleanup_technician_assignments(self):
        """Clean up technician assignments before deletion."""
        if self.default_technician:
            technician_doc = frappe.db.exists("Technician", {"user": self.default_technician})
            if technician_doc:
                frappe.db.set_value("Technician", technician_doc, "current_bench", None)

    # ------------------------------------------------------------
    # PUBLIC API METHODS
    # ------------------------------------------------------------
    @frappe.whitelist()
    def get_current_workload(self) -> dict:
        """Get current workload statistics for this bench."""
        repairs_in_progress = frappe.db.count("Repair Order", {
            "bench": self.name,
            "status": "In Progress"
        })
        
        repairs_pending = frappe.db.count("Repair Order", {
            "bench": self.name,
            "status": "Pending"
        })
        
        total_repairs_today = frappe.db.count("Repair Order", {
            "bench": self.name,
            "creation": (">=", frappe.utils.today())
        })
        
        return {
            "repairs_in_progress": repairs_in_progress,
            "repairs_pending": repairs_pending,
            "total_repairs_today": total_repairs_today,
            "technician": self.default_technician,
            "location": self.location
        }

    @frappe.whitelist()
    def assign_repair(self, repair_order: str) -> bool:
        """Assign a repair order to this bench."""
        if not frappe.has_permission("Repair Order", "write", repair_order):
            frappe.throw(_("Insufficient permissions to assign repair order"))
            
        frappe.db.set_value("Repair Order", repair_order, "bench", self.name)
        
        # If bench has a default technician, assign them too
        if self.default_technician:
            frappe.db.set_value("Repair Order", repair_order, "technician", self.default_technician)
            
        frappe.msgprint(_("Repair Order {0} assigned to bench {1}").format(repair_order, self.name))
        return True

    @frappe.whitelist()
    def get_availability_status(self) -> dict:
        """Get real-time availability status of this bench."""
        current_capacity = self.get_current_workload()
        
        # Simple capacity logic - can be made more sophisticated
        max_concurrent_repairs = 3  # Could be configurable
        
        is_available = current_capacity["repairs_in_progress"] < max_concurrent_repairs
        utilization = (current_capacity["repairs_in_progress"] / max_concurrent_repairs) * 100
        
        return {
            "available": is_available,
            "utilization_percentage": min(utilization, 100),
            "current_repairs": current_capacity["repairs_in_progress"],
            "max_capacity": max_concurrent_repairs,
            "technician_available": bool(self.default_technician),
            "next_available_slot": self._calculate_next_available_slot()
        }

    def _calculate_next_available_slot(self) -> str:
        """Calculate when this bench will next be available."""
        # Simplified logic - would integrate with scheduling system
        if self.get_current_workload()["repairs_in_progress"] == 0:
            return frappe.utils.now()
        
        # Estimate based on average repair time
        estimated_hours = 2  # Average repair time
        return frappe.utils.add_to_date(frappe.utils.now(), hours=estimated_hours)