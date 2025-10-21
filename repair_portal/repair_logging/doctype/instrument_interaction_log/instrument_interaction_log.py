# Path: repair_portal/repair_logging/doctype/instrument_interaction_log/instrument_interaction_log.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready instrument interaction tracking with audit compliance, permission validation, and data integrity
# Dependencies: frappe, frappe.model.document, frappe.utils

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime


class InstrumentInteractionLog(Document):
    """
    Instrument Interaction Log: Track all interactions with instruments for audit and analysis.
    """

    def validate(self):
        """Validate instrument interaction with comprehensive business rules."""
        self._validate_required_fields()
        self._validate_instrument_reference()
        self._validate_user_permissions()
        self._validate_interaction_type()
        self._validate_interaction_data()

    def before_insert(self):
        """Set defaults and process interaction data."""
        self._set_interaction_timestamp()
        self._set_user_context()
        self._normalize_interaction_data()
        self._log_interaction_audit()

    def before_save(self):
        """Update calculations and validations before saving."""
        self._update_interaction_metadata()
        self._validate_data_consistency()

    def on_submit(self):
        """Process interaction completion with proper validation."""
        self._validate_interaction_completion()
        self._update_instrument_interaction_count()
        self._process_interaction_consequences()

    def _validate_required_fields(self):
        """Validate all required fields are present."""
        required_fields = ["interaction_type"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_instrument_reference(self):
        """Validate instrument reference and access permissions."""
        if self.instrument_id and not frappe.db.exists("Instrument Profile", self.instrument_id):
            frappe.throw(_("Instrument {0} does not exist in the system").format(self.instrument_id))

        # Check read permission on instrument if specified
        if self.instrument_id and not frappe.has_permission("Instrument Profile", "read", self.instrument_id):
            frappe.throw(_("No permission to access instrument {0}").format(self.instrument_id))

    def _validate_user_permissions(self):
        """Validate user has appropriate permissions for the interaction type."""
        restricted_interactions = ["Calibration", "Maintenance", "Repair", "Diagnostic"]

        if self.interaction_type in restricted_interactions:
            required_roles = ["Technician", "Maintenance Engineer", "System Manager"]
            user_roles = frappe.get_roles(frappe.session.user)

            if not any(role in user_roles for role in required_roles):
                frappe.throw(
                    _("Insufficient permissions for {0} interaction type").format(self.interaction_type)
                )

    def _validate_interaction_type(self):
        """Validate interaction type is valid."""
        valid_types = [
            "Inspection",
            "Maintenance",
            "Repair",
            "Calibration",
            "Testing",
            "Diagnostic",
            "Cleaning",
            "Setup",
            "Documentation",
            "Other",
        ]

        if self.interaction_type and self.interaction_type not in valid_types:
            frappe.throw(
                _("Invalid interaction type: {0}. Valid options are: {1}").format(
                    self.interaction_type, ", ".join(valid_types)
                )
            )

    def _validate_interaction_data(self):
        """Validate interaction data format and content."""
        # Validate JSON fields
        if self.interaction_details:
            try:
                json.loads(self.interaction_details)
            except json.JSONDecodeError:
                frappe.throw(_("Interaction details must be valid JSON format"))

        # Validate duration if provided
        if self.duration_minutes and (
            float(self.duration_minutes) < 0 or float(self.duration_minutes) > 1440
        ):
            frappe.throw(_("Duration must be between 0 and 1440 minutes (24 hours)"))

        # Validate outcome if provided
        valid_outcomes = ["Success", "Partial Success", "Failed", "Incomplete", "Cancelled"]
        if self.outcome and self.outcome not in valid_outcomes:
            frappe.throw(
                _("Invalid outcome: {0}. Valid options are: {1}").format(
                    self.outcome, ", ".join(valid_outcomes)
                )
            )

    def _set_interaction_timestamp(self):
        """Set interaction timestamp if not specified."""
        if not self.interaction_timestamp:
            self.interaction_timestamp = now_datetime()

    def _set_user_context(self):
        """Set user context for the interaction."""
        if not self.performed_by:
            self.performed_by = frappe.session.user

        # Set session context
        self.session_user = frappe.session.user
        self.user_ip = frappe.local.request_ip if hasattr(frappe.local, "request_ip") else None

    def _normalize_interaction_data(self):
        """Normalize and structure interaction data."""
        # Create structured interaction summary
        interaction_summary = {
            "type": self.interaction_type,
            "timestamp": str(self.interaction_timestamp),
            "performed_by": self.performed_by,
            "duration": self.duration_minutes,
            "outcome": self.outcome,
        }

        # Add to interaction metadata
        if not self.interaction_metadata:
            self.interaction_metadata = json.dumps(interaction_summary, indent=2, default=str)

    def _update_interaction_metadata(self):
        """Update interaction metadata with current values."""
        try:
            metadata = json.loads(self.interaction_metadata or "{}")
            metadata.update({"last_modified": str(now_datetime()), "modified_by": frappe.session.user})
            self.interaction_metadata = json.dumps(metadata, indent=2, default=str)
        except json.JSONDecodeError:
            # Reset metadata if corrupted
            self._normalize_interaction_data()

    def _validate_data_consistency(self):
        """Validate data consistency and integrity."""
        # Check for suspicious duplicate interactions
        if self.interaction_type and self.instrument_id and self.interaction_timestamp:
            # Allow some tolerance for timestamp duplicates (1 minute)
            from frappe.utils import add_to_date

            time_window_start = add_to_date(self.interaction_timestamp, minutes=-1)
            time_window_end = add_to_date(self.interaction_timestamp, minutes=1)

            existing = frappe.db.exists(
                self.doctype,
                {
                    "name": ["!=", self.name],
                    "interaction_type": self.interaction_type,
                    "instrument_id": self.instrument_id,
                    "interaction_timestamp": ["between", [time_window_start, time_window_end]],
                },
            )

            if existing:
                frappe.msgprint(_("Warning: Similar interaction recorded recently: {0}").format(existing))

    def _validate_interaction_completion(self):
        """Validate interaction is complete before submission."""
        if not self.performed_by:
            frappe.throw(_("Performed by field is required for submission"))

        if not self.interaction_timestamp:
            frappe.throw(_("Interaction timestamp is required for submission"))

        if self.outcome == "Failed" and not self.notes:
            frappe.throw(_("Notes are required for failed interactions"))

    def _update_instrument_interaction_count(self):
        """Update instrument's interaction count and last interaction date."""
        if not self.instrument_id:
            return

        try:
            instrument = frappe.get_doc("Instrument Profile", self.instrument_id)

            # Update last interaction date
            if hasattr(instrument, "last_interaction_date"):
                instrument.db_set("last_interaction_date", getdate(self.interaction_timestamp))

            # Increment interaction count
            if hasattr(instrument, "total_interactions"):
                current_count = instrument.total_interactions or 0
                instrument.db_set("total_interactions", current_count + 1)

            frappe.logger("interaction_tracking").info(
                {
                    "action": "instrument_interaction_count_updated",
                    "instrument": self.instrument_id,
                    "interaction_type": self.interaction_type,
                    "new_count": (instrument.total_interactions or 0) + 1,
                }
            )

        except Exception as e:
            frappe.log_error(f"Failed to update instrument interaction count: {str(e)}")

    def _process_interaction_consequences(self):
        """Process consequences of the interaction."""
        # Create follow-up tasks based on interaction outcome
        if self.outcome == "Failed" and self.interaction_type in ["Calibration", "Maintenance"]:
            self._create_follow_up_task()

        # Update instrument status based on interaction
        if self.interaction_type == "Maintenance" and self.outcome == "Success":
            self._update_maintenance_status()

    def _create_follow_up_task(self):
        """Create follow-up task for failed interactions."""
        try:
            follow_up = frappe.get_doc(
                {
                    "doctype": "ToDo",
                    "description": f"Follow-up required for failed {self.interaction_type} on {self.instrument_id}",
                    "reference_type": self.doctype,
                    "reference_name": self.name,
                    "assigned_by": frappe.session.user,
                    "priority": "High" if self.interaction_type in ["Calibration", "Repair"] else "Medium",
                }
            )
            follow_up.insert()

            frappe.logger("interaction_tracking").info(
                {
                    "action": "follow_up_task_created",
                    "task": follow_up.name,
                    "interaction": self.name,
                    "reason": "failed_interaction",
                }
            )

        except Exception as e:
            frappe.log_error(f"Failed to create follow-up task: {str(e)}")

    def _update_maintenance_status(self):
        """Update instrument maintenance status."""
        if not self.instrument_id:
            return

        try:
            instrument = frappe.get_doc("Instrument Profile", self.instrument_id)

            if hasattr(instrument, "last_maintenance_date"):
                instrument.db_set("last_maintenance_date", getdate(self.interaction_timestamp))

            if hasattr(instrument, "maintenance_status"):
                instrument.db_set("maintenance_status", "Up to Date")

        except Exception as e:
            frappe.log_error(f"Failed to update maintenance status: {str(e)}")

    def _log_interaction_audit(self):
        """Log interaction for audit compliance."""
        frappe.logger("interaction_audit").info(
            {
                "action": "instrument_interaction",
                "instrument_id": self.instrument_id,
                "interaction_type": self.interaction_type,
                "performed_by": self.performed_by,
                "session_user": frappe.session.user,
                "timestamp": str(self.interaction_timestamp),
                "user_ip": getattr(frappe.local, "request_ip", None),
            }
        )

    @frappe.whitelist()
    def add_follow_up_note(self, note):
        """Add follow-up note to the interaction."""
        if not frappe.has_permission(self.doctype, "write", self.name):
            frappe.throw(_("No permission to add notes"))

        if not note or not note.strip():
            frappe.throw(_("Note cannot be empty"))

        # Append to existing notes
        current_notes = self.notes or ""
        timestamp = now_datetime().strftime("%Y-%m-%d %H:%M:%S")
        new_note = f"\n[{timestamp} - {frappe.session.user}]: {note.strip()}"

        self.db_set("notes", current_notes + new_note)

        frappe.logger("interaction_tracking").info(
            {"action": "follow_up_note_added", "interaction": self.name, "user": frappe.session.user}
        )

        return {"message": "Note added successfully"}

    @frappe.whitelist()
    def get_interaction_history(self):
        """Get interaction history for the instrument."""
        if self.instrument_id and not frappe.has_permission("Instrument Profile", "read", self.instrument_id):
            frappe.throw(_("No permission to view interaction history"))

        if not self.instrument_id:
            return []

        interactions = frappe.get_all(
            self.doctype,
            filters={"instrument_id": self.instrument_id},
            fields=["name", "interaction_type", "interaction_timestamp", "performed_by", "outcome"],
            order_by="interaction_timestamp desc",
            limit=50,
        )

        return interactions
