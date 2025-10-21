# Path: repair_portal/repair_logging/doctype/tool_usage_log/tool_usage_log.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready tool usage tracking with calibration validation and audit compliance
# Dependencies: frappe, frappe.model.document, frappe.utils

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime, time_diff_in_hours


class ToolUsageLog(Document):
    """
    Tool Usage Log: Track tool usage during repair operations with calibration compliance and audit trail.
    Essential for tool lifecycle management and quality assurance.
    """

    def validate(self):
        """Validate tool usage data with comprehensive business rules."""
        self._validate_required_fields()
        self._validate_tool_reference()
        self._validate_user_permissions()
        self._validate_usage_timing()
        self._validate_calibration_status()

    def before_insert(self):
        """Set defaults and validate usage setup."""
        self._set_usage_timestamp()
        self._normalize_usage_data()
        self._validate_tool_availability()
        self._log_usage_audit()

    def before_save(self):
        """Update calculations and validations before saving."""
        self._calculate_usage_duration()
        self._update_usage_metadata()
        self._validate_usage_consistency()

    def on_submit(self):
        """Process usage completion with proper validation."""
        self._validate_usage_completion()
        self._update_tool_status()
        self._check_maintenance_requirements()
        self._update_tool_lifecycle()

    def _validate_required_fields(self):
        """Validate all required usage fields are present."""
        required_fields = ["tool", "used_by", "usage_type"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_tool_reference(self):
        """Validate tool reference exists and is accessible."""
        if self.tool:
            if not frappe.db.exists("Tool", self.tool):
                frappe.throw(_("Tool {0} does not exist").format(self.tool))

            if not frappe.has_permission("Tool", "read", self.tool):
                frappe.throw(_("No permission to access tool {0}").format(self.tool))

            # Get tool details for validation context
            tool_data = frappe.db.get_value(
                "Tool", self.tool, ["tool_name", "tool_type", "status", "calibration_due_date"], as_dict=True
            )

            if tool_data:
                self.tool_name = tool_data.tool_name
                self.tool_type = tool_data.tool_type

                # Check tool availability
                if tool_data.status not in ["Available", "In Use"]:
                    frappe.throw(
                        _("Tool {0} is not available for use (Status: {1})").format(
                            self.tool, tool_data.status
                        )
                    )

    def _validate_user_permissions(self):
        """Validate user has appropriate permissions for tool usage."""
        if self.used_by:
            # Verify user exists and is active
            user_data = frappe.db.get_value("User", self.used_by, ["enabled", "full_name"])

            if not user_data or not user_data[0]:
                frappe.throw(_("User {0} is not active in the system.").format(self.used_by))

            # Check for appropriate tool usage roles
            required_roles = ["Technician", "Tool Operator", "Repair Specialist", "System Manager"]
            user_roles = frappe.get_roles(self.used_by)

            if not any(role in user_roles for role in required_roles):
                frappe.throw(
                    _("User {0} does not have appropriate permissions for tool usage.").format(self.used_by)
                )

    def _validate_usage_timing(self):
        """Validate usage timing and duration."""
        # Validate start time
        if self.start_time:
            start_datetime = self.start_time
            if start_datetime > now_datetime():
                frappe.throw(_("Start time cannot be in the future"))

        # Validate end time if specified
        if self.end_time:
            end_datetime = self.end_time
            if self.start_time and end_datetime < self.start_time:
                frappe.throw(_("End time cannot be before start time"))

            if end_datetime > now_datetime():
                frappe.throw(_("End time cannot be in the future"))

        # Validate planned duration
        if self.planned_duration:
            duration = flt(self.planned_duration)
            if duration <= 0:
                frappe.throw(_("Planned duration must be positive"))
            if duration > 480:  # 8 hours in minutes
                frappe.msgprint(_("Warning: Planned duration {0} minutes exceeds 8 hours").format(duration))

    def _validate_calibration_status(self):
        """Validate tool calibration status for critical measurements."""
        if not self.tool:
            return

        tool_data = frappe.db.get_value(
            "Tool", self.tool, ["requires_calibration", "calibration_due_date", "tool_type"], as_dict=True
        )

        if tool_data and tool_data.requires_calibration:
            if tool_data.calibration_due_date:
                due_date = getdate(tool_data.calibration_due_date)
                today = getdate()

                if due_date < today:
                    frappe.throw(_("Tool {0} calibration is overdue (Due: {1})").format(self.tool, due_date))
                elif (due_date - today).days <= 7:
                    frappe.msgprint(
                        _("Warning: Tool {0} calibration due soon ({1})").format(self.tool, due_date)
                    )
            else:
                frappe.msgprint(
                    _("Warning: Tool {0} requires calibration but no due date set").format(self.tool)
                )

    def _set_usage_timestamp(self):
        """Set usage timestamp if not specified."""
        if not self.start_time:
            self.start_time = now_datetime()

    def _normalize_usage_data(self):
        """Normalize and structure usage data."""
        # Validate usage type
        valid_usage_types = [
            "Measurement",
            "Cutting",
            "Drilling",
            "Sanding",
            "Polishing",
            "Assembly",
            "Disassembly",
            "Calibration",
            "Testing",
            "Cleaning",
            "Maintenance",
            "Other",
        ]

        if self.usage_type and self.usage_type not in valid_usage_types:
            frappe.throw(
                _("Invalid usage type: {0}. Valid options are: {1}").format(
                    self.usage_type, ", ".join(valid_usage_types)
                )
            )

        # Create structured usage summary
        usage_summary = {
            "tool": self.tool,
            "tool_name": self.tool_name,
            "tool_type": self.tool_type,
            "usage_type": self.usage_type,
            "used_by": self.used_by,
            "start_time": str(self.start_time),
            "planned_duration": self.planned_duration,
        }

        # Store usage metadata
        if not self.usage_metadata:
            self.usage_metadata = json.dumps(usage_summary, indent=2, default=str)

    def _validate_tool_availability(self):
        """Validate tool is available for use."""
        if not self.tool:
            return

        # Check for concurrent usage
        concurrent_usage = frappe.get_all(
            "Tool Usage Log",
            filters={
                "tool": self.tool,
                "docstatus": ["!=", 2],
                "end_time": ["is", "not set"],
                "name": ["!=", self.name or ""],
            },
            fields=["name", "used_by", "start_time"],
        )

        if concurrent_usage:
            current_user = concurrent_usage[0]
            frappe.throw(
                _("Tool {0} is currently in use by {1} (Started: {2})").format(
                    self.tool, current_user.used_by, current_user.start_time
                )
            )

    def _calculate_usage_duration(self):
        """Calculate actual usage duration."""
        if self.start_time and self.end_time:
            # Calculate duration in hours
            duration_hours = time_diff_in_hours(self.end_time, self.start_time)

            # Convert to minutes for storage
            self.actual_duration = duration_hours * 60

            # Calculate variance if planned duration specified
            if self.planned_duration:
                planned_minutes = flt(self.planned_duration)
                actual_minutes = flt(self.actual_duration)

                if planned_minutes > 0:
                    variance_percentage = ((actual_minutes - planned_minutes) / planned_minutes) * 100
                    self.duration_variance = variance_percentage

    def _update_usage_metadata(self):
        """Update usage metadata with current values."""
        try:
            metadata = json.loads(self.usage_metadata or "{}")
            metadata.update(
                {
                    "last_modified": str(now_datetime()),
                    "modified_by": frappe.session.user,
                    "end_time": str(self.end_time) if self.end_time else None,
                    "actual_duration": self.actual_duration,
                    "duration_variance": self.duration_variance,
                    "usage_notes": self.usage_notes,
                }
            )
            self.usage_metadata = json.dumps(metadata, indent=2, default=str)
        except json.JSONDecodeError:
            # Reset metadata if corrupted
            self._normalize_usage_data()

    def _validate_usage_consistency(self):
        """Validate usage data consistency."""
        # Check for reasonable duration
        if self.actual_duration:
            duration_minutes = flt(self.actual_duration)

            if duration_minutes > 480:  # 8 hours
                frappe.msgprint(
                    _("Warning: Usage duration {0} minutes exceeds 8 hours").format(duration_minutes)
                )
            elif duration_minutes < 1:
                frappe.msgprint(
                    _("Warning: Usage duration {0} minutes is very short").format(duration_minutes)
                )

    def _validate_usage_completion(self):
        """Validate usage is complete before submission."""
        if not self.end_time:
            frappe.throw(_("End time is required for submission"))

        if not self.actual_duration:
            frappe.throw(_("Actual duration must be calculated for submission"))

        # Require notes for extended usage
        if self.actual_duration and flt(self.actual_duration) > 240 and not self.usage_notes:  # 4 hours
            frappe.throw(_("Usage notes are required for extended tool usage (>4 hours)"))

    def _update_tool_status(self):
        """Update tool status based on usage completion."""
        if not self.tool:
            return

        try:
            tool_doc = frappe.get_doc("Tool", self.tool)

            # Update last used information
            if hasattr(tool_doc, "last_used_date"):
                tool_doc.db_set("last_used_date", getdate())

            if hasattr(tool_doc, "last_used_by"):
                tool_doc.db_set("last_used_by", self.used_by)

            # Update usage hours if tracked
            if hasattr(tool_doc, "total_usage_hours") and self.actual_duration:
                current_hours = flt(tool_doc.total_usage_hours or 0)
                additional_hours = flt(self.actual_duration) / 60
                new_total = current_hours + additional_hours
                tool_doc.db_set("total_usage_hours", new_total)

            frappe.logger("tool_usage_tracking").info(
                {
                    "action": "tool_usage_completed",
                    "tool": self.tool,
                    "used_by": self.used_by,
                    "duration_minutes": self.actual_duration,
                    "usage_type": self.usage_type,
                }
            )

        except Exception as e:
            frappe.log_error(f"Failed to update tool status: {str(e)}")

    def _check_maintenance_requirements(self):
        """Check if tool maintenance is required after usage."""
        if not (self.tool and self.actual_duration):
            return

        try:
            tool_data = frappe.db.get_value(
                "Tool",
                self.tool,
                ["maintenance_schedule", "total_usage_hours", "next_maintenance_hours"],
                as_dict=True,
            )

            if tool_data and tool_data.next_maintenance_hours:
                current_hours = flt(tool_data.total_usage_hours or 0)
                maintenance_due_hours = flt(tool_data.next_maintenance_hours)

                if current_hours >= maintenance_due_hours:
                    frappe.msgprint(
                        _("Tool {0} requires scheduled maintenance (Usage: {1} hours)").format(
                            self.tool, current_hours
                        ),
                        alert=True,
                    )

                    # Log maintenance alert
                    frappe.logger("tool_maintenance_alerts").warning(
                        {
                            "action": "maintenance_required",
                            "tool": self.tool,
                            "current_usage_hours": current_hours,
                            "maintenance_due_hours": maintenance_due_hours,
                            "last_used_by": self.used_by,
                        }
                    )

        except Exception as e:
            frappe.log_error(f"Failed to check maintenance requirements: {str(e)}")

    def _update_tool_lifecycle(self):
        """Update tool lifecycle tracking."""
        if not self.tool:
            return

        try:
            # Create lifecycle entry
            lifecycle_record = {
                "usage_log_id": self.name,
                "tool": self.tool,
                "usage_type": self.usage_type,
                "used_by": self.used_by,
                "duration_minutes": self.actual_duration,
                "start_time": str(self.start_time),
                "end_time": str(self.end_time),
                "usage_notes": self.usage_notes,
            }

            frappe.logger("tool_lifecycle").info(
                {"action": "usage_recorded", "lifecycle_data": lifecycle_record}
            )

        except Exception as e:
            frappe.log_error(f"Failed to update tool lifecycle: {str(e)}")

    def _log_usage_audit(self):
        """Log tool usage for audit compliance."""
        frappe.logger("tool_usage_audit").info(
            {
                "action": "tool_usage_started",
                "tool": self.tool,
                "tool_name": self.tool_name,
                "tool_type": self.tool_type,
                "usage_type": self.usage_type,
                "used_by": self.used_by,
                "start_time": str(self.start_time),
                "planned_duration": self.planned_duration,
                "user": frappe.session.user,
                "timestamp": str(now_datetime()),
            }
        )

    @frappe.whitelist()
    def complete_usage(self):
        """Complete tool usage with proper validation."""
        if not frappe.has_permission(self.doctype, "write"):
            frappe.throw(_("No permission to complete tool usage"))

        if self.end_time:
            frappe.throw(_("Tool usage already completed"))

        # Set end time and calculate duration
        self.end_time = now_datetime()
        self._calculate_usage_duration()
        self._update_usage_metadata()

        # Save changes
        self.save()

        return {
            "end_time": self.end_time,
            "actual_duration": self.actual_duration,
            "duration_variance": self.duration_variance,
        }

    @frappe.whitelist()
    def get_tool_usage_history(self):
        """Get usage history for this tool."""
        if not frappe.has_permission(self.doctype, "read"):
            frappe.throw(_("No permission to view usage history"))

        if not self.tool:
            return []

        history = frappe.get_all(
            self.doctype,
            filters={"tool": self.tool, "docstatus": ["!=", 2]},
            fields=[
                "name",
                "start_time",
                "end_time",
                "usage_type",
                "used_by",
                "actual_duration",
                "usage_notes",
            ],
            order_by="start_time desc",
            limit=50,
        )

        return history
