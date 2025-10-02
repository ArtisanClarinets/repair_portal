# Path: repair_portal/repair_logging/doctype/repair_task_log/repair_task_log.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready repair task logging with time tracking, validation, and audit compliance
# Dependencies: frappe, frappe.model.document, frappe.utils

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime, time_diff_in_hours


class RepairTaskLog(Document):
    """
    Repair Task Log: Track individual repair tasks with time, cost, and quality validation.
    """

    def validate(self):
        """Validate repair task log with comprehensive business rules."""
        self._validate_required_fields()
        self._validate_technician_permissions()
        self._validate_time_tracking()
        self._validate_task_status()
        self._validate_cost_tracking()
        self._set_logged_by_user()

    def before_insert(self):
        """Set defaults and calculate metrics."""
        self._set_default_start_time()
        self._auto_calculate_duration()
        self._log_task_audit()

    def before_save(self):
        """Update calculations before saving."""
        self._auto_calculate_duration()
        self._validate_billable_time()

    def on_submit(self):
        """Process task completion with proper validation."""
        self._validate_task_completion()
        self._update_parent_progress()
        self._log_completion_audit()

    def _validate_required_fields(self):
        """Validate all required fields are present."""
        required_fields = ["task_description"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_technician_permissions(self):
        """Validate technician access and qualifications."""
        if self.technician:
            # Verify technician exists and is active
            technician_data = frappe.db.get_value('User', self.technician, 
                ['enabled', 'full_name'])
            
            if not technician_data or not technician_data[0]:
                frappe.throw(_('Technician {0} is not active in the system.').format(self.technician))
            
            # Check if user has technician role
            if not frappe.db.exists('Has Role', {'parent': self.technician, 'role': 'Technician'}):
                frappe.msgprint(_('Warning: User {0} does not have Technician role.').format(self.technician))

    def _validate_time_tracking(self):
        """Validate time tracking accuracy and logic."""
        if self.start_time and self.end_time:
            if getdate(self.start_time) > getdate(self.end_time):
                frappe.throw(_('End time cannot be before start time.'))
            
            # Calculate duration in hours
            duration = time_diff_in_hours(self.end_time, self.start_time)
            
            if duration < 0:
                frappe.throw(_('Invalid time range: negative duration calculated.'))
            
            # Business rule: Maximum 24 hours per task
            if duration > 24:
                frappe.throw(_('Task duration ({0} hours) exceeds maximum allowed (24 hours).').format(duration))
            
            self.duration_hours = flt(duration, 2)
        
        elif self.duration_hours:
            # Validate manually entered duration
            if flt(self.duration_hours) < 0:
                frappe.throw(_('Duration cannot be negative.'))
            
            if flt(self.duration_hours) > 24:
                frappe.throw(_('Duration cannot exceed 24 hours.'))

    def _validate_task_status(self):
        """Validate task status transitions."""
        valid_statuses = ['Not Started', 'In Progress', 'Completed', 'On Hold', 'Cancelled']
        
        if self.status and self.status not in valid_statuses:
            frappe.throw(_('Invalid status: {0}. Valid options are: {1}').format(
                self.status, ', '.join(valid_statuses)))
        
        # Status-specific validations
        if self.status == 'Completed' and not self.end_time and not self.duration_hours:
            frappe.throw(_('Completed tasks must have end time or duration specified.'))
        
        if self.status in ['In Progress', 'Completed'] and not self.start_time:
            frappe.throw(_('Tasks in progress or completed must have a start time.'))

    def _validate_cost_tracking(self):
        """Validate cost and billing information."""
        if self.hourly_rate and flt(self.hourly_rate) < 0:
            frappe.throw(_('Hourly rate cannot be negative.'))
        
        if self.total_cost and flt(self.total_cost) < 0:
            frappe.throw(_('Total cost cannot be negative.'))
        
        # Validate cost calculation
        if self.hourly_rate and self.duration_hours:
            calculated_cost = flt(self.hourly_rate) * flt(self.duration_hours)
            if self.total_cost and abs(flt(self.total_cost) - calculated_cost) > 0.01:
                frappe.msgprint(_('Warning: Total cost does not match hourly rate × duration.'))

    def _set_logged_by_user(self):
        """Set logged_by user with audit compliance."""
        if not getattr(self, 'logged_by', None):
            self.logged_by = frappe.session.user
        elif self.logged_by != frappe.session.user:
            # SOX/ISO/FDA compliant audit logging for unauthorized attempts
            frappe.logger("security_audit").error({
                "action": "unauthorized_logged_by_attempt",
                "attempted_user": self.logged_by,
                "actual_user": frappe.session.user,
                "document": self.name,
                "timestamp": frappe.utils.now()
            })
            frappe.log_error(
                f'User {frappe.session.user} tried to set logged_by to {self.logged_by}',
                'RepairTaskLog: Unauthorized logged_by attempt',
            )

    def _set_default_start_time(self):
        """Set default start time if not specified."""
        if not self.start_time and self.status in ['In Progress']:
            self.start_time = now_datetime()

    def _auto_calculate_duration(self):
        """Automatically calculate duration from start/end times."""
        if self.start_time and self.end_time and not self.duration_hours:
            duration = time_diff_in_hours(self.end_time, self.start_time)
            self.duration_hours = flt(duration, 2)
        
        # Calculate total cost if rate is available
        if self.hourly_rate and self.duration_hours:
            self.total_cost = flt(self.hourly_rate) * flt(self.duration_hours)

    def _validate_billable_time(self):
        """Validate billable time calculations."""
        if self.billable_hours:
            if flt(self.billable_hours) < 0:
                frappe.throw(_('Billable hours cannot be negative.'))
            
            if self.duration_hours and flt(self.billable_hours) > flt(self.duration_hours):
                frappe.throw(_('Billable hours ({0}) cannot exceed total duration ({1}).').format(
                    self.billable_hours, self.duration_hours))

    def _validate_task_completion(self):
        """Validate task is properly completed before submission."""
        if self.status != 'Completed':
            frappe.throw(_('Only completed tasks can be submitted.'))
        
        if not self.end_time and not self.duration_hours:
            frappe.throw(_('Completed tasks must have end time or duration.'))
        
        # Quality check validation
        if self.quality_rating and (flt(self.quality_rating) < 1 or flt(self.quality_rating) > 5):
            frappe.throw(_('Quality rating must be between 1 and 5.'))

    def _update_parent_progress(self):
        """Update parent document progress based on task completion."""
        if self.parent and self.parenttype:
            try:
                parent_doc = frappe.get_doc(self.parenttype, self.parent)
                
                # Calculate completion percentage
                total_tasks = frappe.db.count(self.doctype, {'parent': self.parent})
                completed_tasks = frappe.db.count(self.doctype, {
                    'parent': self.parent, 
                    'status': 'Completed'
                })
                
                completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                
                # Update parent if it has progress tracking
                if hasattr(parent_doc, 'progress_percentage'):
                    parent_doc.db_set('progress_percentage', completion_percentage)
                
                frappe.logger("task_progress").info({
                    "action": "progress_updated",
                    "parent_document": self.parent,
                    "completion_percentage": completion_percentage,
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks
                })
                
            except Exception as e:
                frappe.log_error(f"Failed to update parent progress: {str(e)}")

    def _log_task_audit(self):
        """Log task creation for audit compliance."""
        frappe.logger("task_tracking").info({
            "action": "task_created",
            "task_description": self.task_description,
            "technician": self.technician,
            "logged_by": self.logged_by,
            "parent_document": self.parent,
            "user": frappe.session.user,
            "timestamp": frappe.utils.now()
        })

    def _log_completion_audit(self):
        """Log task completion for audit compliance."""
        frappe.logger("task_tracking").info({
            "action": "task_completed",
            "task_description": self.task_description,
            "technician": self.technician,
            "duration_hours": self.duration_hours,
            "total_cost": self.total_cost,
            "quality_rating": self.quality_rating,
            "user": frappe.session.user,
            "timestamp": frappe.utils.now()
        })

    @frappe.whitelist()
    def start_task(self):
        """Start task timing with validation."""
        if not frappe.has_permission(self.doctype, "write", self.name):
            frappe.throw(_("No permission to start task"))
        
        if self.status == 'Completed':
            frappe.throw(_("Cannot start a completed task"))
        
        self.start_time = now_datetime()
        self.status = 'In Progress'
        self.save()
        
        frappe.logger("task_tracking").info({
            "action": "task_started",
            "task": self.name,
            "technician": self.technician,
            "start_time": self.start_time
        })
        
        return {"message": "Task started successfully"}

    @frappe.whitelist()
    def end_task(self):
        """End task timing with validation."""
        if not frappe.has_permission(self.doctype, "write", self.name):
            frappe.throw(_("No permission to end task"))
        
        if not self.start_time:
            frappe.throw(_("Cannot end task that was never started"))
        
        self.end_time = now_datetime()
        self.status = 'Completed'
        self._auto_calculate_duration()
        self.save()
        
        frappe.logger("task_tracking").info({
            "action": "task_ended",
            "task": self.name,
            "technician": self.technician,
            "end_time": self.end_time,
            "duration": self.duration_hours
        })
        
        return {"message": "Task completed successfully", "duration": self.duration_hours}
