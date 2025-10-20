# Path: repair_portal/repair_logging/doctype/warranty_modification_log/warranty_modification_log.py
# Date: 2025-01-14
# Version: 2.0.0
# Description: Production-ready warranty modification tracking with compliance validation and audit trail
# Dependencies: frappe, frappe.model.document, frappe.utils

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, flt, getdate, now_datetime


class WarrantyModificationLog(Document):
    """
    Warranty Modification Log: Track all warranty changes with comprehensive audit trail and compliance validation.
    Critical for warranty management and regulatory compliance.
    """

    def validate(self):
        """Validate warranty modification data with comprehensive business rules."""
        self._validate_required_fields()
        self._validate_instrument_reference()
        self._validate_modification_data()
        self._validate_authorization()
        self._validate_date_logic()

    def before_insert(self):
        """Set defaults and validate modification setup."""
        self._set_modification_timestamp()
        self._normalize_modification_data()
        self._validate_modification_authority()
        self._log_modification_audit()

    def before_save(self):
        """Update calculations and validations before saving."""
        self._calculate_warranty_impact()
        self._update_modification_metadata()
        self._validate_modification_consistency()

    def on_submit(self):
        """Process modification completion with proper validation."""
        self._validate_modification_completion()
        self._update_instrument_warranty()
        self._check_compliance_requirements()
        self._generate_modification_certificate()

    def _validate_required_fields(self):
        """Validate all required modification fields are present."""
        required_fields = ["modification_type", "authorized_by", "effective_date"]
        missing = [field for field in required_fields if not self.get(field)]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_instrument_reference(self):
        """Validate instrument reference exists and is accessible."""
        if self.instrument_profile:
            if not frappe.db.exists("Instrument Profile", self.instrument_profile):
                frappe.throw(_("Instrument Profile {0} does not exist").format(self.instrument_profile))

            if not frappe.has_permission("Instrument Profile", "read", self.instrument_profile):
                frappe.throw(_("No permission to access instrument {0}").format(self.instrument_profile))

            # Get instrument details for validation context
            instrument_data = frappe.db.get_value(
                "Instrument Profile",
                self.instrument_profile,
                ["instrument_type", "serial_number", "warranty_start_date", "warranty_end_date"],
                as_dict=True,
            )

            if instrument_data:
                self.instrument_type = instrument_data.instrument_type
                self.instrument_serial = instrument_data.serial_number
                self.original_warranty_start = instrument_data.warranty_start_date
                self.original_warranty_end = instrument_data.warranty_end_date

    def _validate_modification_data(self):
        """Validate modification type and parameters."""
        # Validate modification type
        valid_modification_types = [
            "Extension",
            "Reduction",
            "Transfer",
            "Cancellation",
            "Reinstatement",
            "Upgrade Coverage",
            "Downgrade Coverage",
            "Terms Update",
            "Administrative Correction",
        ]

        if self.modification_type and self.modification_type not in valid_modification_types:
            frappe.throw(
                _("Invalid modification type: {0}. Valid options are: {1}").format(
                    self.modification_type, ", ".join(valid_modification_types)
                )
            )

        # Validate modification reason
        if self.modification_reason:
            valid_reasons = [
                "Customer Request",
                "Service Credit",
                "Goodwill Gesture",
                "Repair Quality Issue",
                "Manufacturing Defect",
                "Regulatory Compliance",
                "Business Policy Change",
                "Administrative Error",
                "Legal Settlement",
                "Insurance Claim",
            ]

            if self.modification_reason not in valid_reasons:
                frappe.msgprint(
                    _("Warning: Non-standard modification reason: {0}").format(self.modification_reason)
                )

    def _validate_authorization(self):
        """Validate authorization and approval requirements."""
        if self.authorized_by:
            # Verify authorizer exists and is active
            auth_data = frappe.db.get_value("User", self.authorized_by, ["enabled", "full_name"])

            if not auth_data or not auth_data[0]:
                frappe.throw(_("Authorizer {0} is not active in the system.").format(self.authorized_by))

            # Check for appropriate authorization roles
            required_roles = ["Warranty Manager", "Service Manager", "Regional Manager", "System Manager"]
            user_roles = frappe.get_roles(self.authorized_by)

            if not any(role in user_roles for role in required_roles):
                frappe.throw(
                    _(
                        "User {0} does not have appropriate permissions to authorize warranty modifications."
                    ).format(self.authorized_by)
                )

        # Validate approval requirements for significant modifications
        if (
            self.modification_type in ["Extension", "Upgrade Coverage", "Reinstatement"]
            and not self.approval_reference
        ):
            frappe.msgprint(
                _("Warning: Approval reference recommended for {0}").format(self.modification_type)
            )

    def _validate_date_logic(self):
        """Validate date logic and constraints."""
        # Validate effective date
        if self.effective_date:
            effective = getdate(self.effective_date)
            today = getdate()

            # Allow future dates for scheduled modifications
            if effective < today and not self.retroactive_approval:
                frappe.throw(_("Effective date cannot be in the past without retroactive approval"))

        # Validate new warranty dates if specified
        if self.new_warranty_start_date and self.new_warranty_end_date:
            start_date = getdate(self.new_warranty_start_date)
            end_date = getdate(self.new_warranty_end_date)

            if end_date <= start_date:
                frappe.throw(_("New warranty end date must be after start date"))

            # Check for reasonable warranty periods
            warranty_days = date_diff(end_date, start_date)

            if warranty_days > 3650:  # 10 years
                frappe.msgprint(_("Warning: Warranty period {0} days exceeds 10 years").format(warranty_days))
            elif warranty_days < 30:  # 30 days
                frappe.msgprint(
                    _("Warning: Warranty period {0} days is less than 30 days").format(warranty_days)
                )

    def _set_modification_timestamp(self):
        """Set modification timestamp if not specified."""
        if not self.modification_timestamp:
            self.modification_timestamp = now_datetime()

    def _normalize_modification_data(self):
        """Normalize and structure modification data."""
        # Create structured modification summary
        modification_summary = {
            "instrument_profile": self.instrument_profile,
            "modification_type": self.modification_type,
            "modification_reason": self.modification_reason,
            "authorized_by": self.authorized_by,
            "effective_date": str(self.effective_date),
            "original_start": str(self.original_warranty_start) if self.original_warranty_start else None,
            "original_end": str(self.original_warranty_end) if self.original_warranty_end else None,
            "new_start": str(self.new_warranty_start_date) if self.new_warranty_start_date else None,
            "new_end": str(self.new_warranty_end_date) if self.new_warranty_end_date else None,
            "timestamp": str(self.modification_timestamp),
        }

        # Store modification metadata
        if not self.modification_metadata:
            self.modification_metadata = json.dumps(modification_summary, indent=2, default=str)

    def _validate_modification_authority(self):
        """Validate modification authority and business rules."""
        # Check for conflicting modifications
        if self.instrument_profile and self.effective_date:
            conflicting_mods = frappe.get_all(
                self.doctype,
                filters={
                    "instrument_profile": self.instrument_profile,
                    "effective_date": self.effective_date,
                    "docstatus": ["!=", 2],
                    "name": ["!=", self.name or ""],
                },
                fields=["name", "modification_type", "authorized_by"],
            )

            if conflicting_mods:
                frappe.msgprint(
                    _("Warning: Conflicting modification on same date: {0}").format(conflicting_mods[0].name)
                )

    def _calculate_warranty_impact(self):
        """Calculate warranty impact and changes."""
        if not (self.original_warranty_end and self.new_warranty_end_date):
            return

        original_end = getdate(self.original_warranty_end)
        new_end = getdate(self.new_warranty_end_date)

        # Calculate extension/reduction in days
        impact_days = date_diff(new_end, original_end)
        self.warranty_impact_days = impact_days

        # Determine impact type
        if impact_days > 0:
            self.impact_type = f"Extension of {impact_days} days"
        elif impact_days < 0:
            self.impact_type = f"Reduction of {abs(impact_days)} days"
        else:
            self.impact_type = "No change in warranty period"

        # Calculate cost impact if rates available
        if self.daily_warranty_cost and impact_days:
            cost_impact = flt(self.daily_warranty_cost) * abs(impact_days)
            if impact_days > 0:
                self.cost_impact = cost_impact
                self.cost_impact_type = "Additional Cost"
            else:
                self.cost_impact = cost_impact
                self.cost_impact_type = "Cost Savings"

    def _update_modification_metadata(self):
        """Update modification metadata with current values."""
        try:
            metadata = json.loads(self.modification_metadata or "{}")
            metadata.update(
                {
                    "last_modified": str(now_datetime()),
                    "modified_by": frappe.session.user,
                    "warranty_impact_days": self.warranty_impact_days,
                    "impact_type": self.impact_type,
                    "cost_impact": self.cost_impact,
                    "approval_reference": self.approval_reference,
                }
            )
            self.modification_metadata = json.dumps(metadata, indent=2, default=str)
        except json.JSONDecodeError:
            # Reset metadata if corrupted
            self._normalize_modification_data()

    def _validate_modification_consistency(self):
        """Validate modification data consistency."""
        # Check logical consistency between modification type and dates
        if self.modification_type == "Extension" and self.warranty_impact_days:
            if self.warranty_impact_days <= 0:
                frappe.msgprint(_("Warning: Extension type but warranty impact is not positive"))

        elif self.modification_type == "Reduction" and self.warranty_impact_days:
            if self.warranty_impact_days >= 0:
                frappe.msgprint(_("Warning: Reduction type but warranty impact is not negative"))

        elif (
            self.modification_type == "Cancellation"
            and self.new_warranty_end_date
            and getdate(self.new_warranty_end_date) > getdate()
        ):
            frappe.msgprint(_("Warning: Cancellation but new end date is in the future"))

    def _validate_modification_completion(self):
        """Validate modification is complete before submission."""
        if not self.authorized_by:
            frappe.throw(_("Authorized by field is required for submission"))

        if not self.effective_date:
            frappe.throw(_("Effective date is required for submission"))

        # Require detailed justification for significant changes
        if (
            self.warranty_impact_days
            and abs(self.warranty_impact_days) > 365
            and not self.detailed_justification
        ):
            frappe.throw(_("Detailed justification is required for warranty changes exceeding 1 year"))

        # Require customer notification for certain types
        if self.modification_type in ["Reduction", "Cancellation"] and not self.customer_notified:
            frappe.msgprint(_("Consider customer notification for {0}").format(self.modification_type))

    def _update_instrument_warranty(self):
        """Update instrument warranty information."""
        if not self.instrument_profile:
            return

        try:
            instrument = frappe.get_doc("Instrument Profile", self.instrument_profile)

            # Update warranty dates if specified
            if self.new_warranty_start_date and hasattr(instrument, "warranty_start_date"):
                instrument.db_set("warranty_start_date", self.new_warranty_start_date)

            if self.new_warranty_end_date and hasattr(instrument, "warranty_end_date"):
                instrument.db_set("warranty_end_date", self.new_warranty_end_date)

            # Update warranty status if field exists
            if hasattr(instrument, "warranty_status"):
                if self.modification_type == "Cancellation":
                    instrument.db_set("warranty_status", "Cancelled")
                elif self.modification_type == "Reinstatement":
                    instrument.db_set("warranty_status", "Active")

            # Log warranty update for instrument history
            warranty_record = {
                "modification_id": self.name,
                "modification_type": self.modification_type,
                "authorized_by": self.authorized_by,
                "effective_date": str(self.effective_date),
                "warranty_impact_days": self.warranty_impact_days,
                "new_start_date": str(self.new_warranty_start_date) if self.new_warranty_start_date else None,
                "new_end_date": str(self.new_warranty_end_date) if self.new_warranty_end_date else None,
            }

            frappe.logger("warranty_modification_history").info(
                {
                    "action": "warranty_modified",
                    "instrument_profile": self.instrument_profile,
                    "modification_data": warranty_record,
                }
            )

        except Exception as e:
            frappe.log_error(f"Failed to update instrument warranty: {str(e)}")

    def _check_compliance_requirements(self):
        """Check compliance requirements for warranty modifications."""
        compliance_alerts = []

        # Check for regulatory compliance requirements
        if (
            self.modification_type in ["Extension", "Upgrade Coverage"]
            and self.warranty_impact_days
            and self.warranty_impact_days > 730
        ):  # 2 years
            compliance_alerts.append("Extended warranty >2 years may require regulatory notification")

        # Check for customer rights compliance
        if self.modification_type in ["Reduction", "Cancellation"]:
            compliance_alerts.append(
                "Customer notification and consent required for warranty reduction/cancellation"
            )

        # Check for documentation requirements
        if self.cost_impact and self.cost_impact > 1000:
            compliance_alerts.append("Financial impact >$1000 requires additional documentation")

        # Generate compliance alerts if needed
        if compliance_alerts:
            alert_message = "Compliance Requirements:\n" + "\n".join(compliance_alerts)
            frappe.msgprint(alert_message, alert=True)

            # Log compliance alerts
            frappe.logger("warranty_compliance").warning(
                {
                    "action": "warranty_modification_compliance_alert",
                    "instrument_profile": self.instrument_profile,
                    "modification_type": self.modification_type,
                    "warranty_impact_days": self.warranty_impact_days,
                    "cost_impact": self.cost_impact,
                    "alerts": compliance_alerts,
                    "authorized_by": self.authorized_by,
                }
            )

    def _generate_modification_certificate(self):
        """Generate modification certificate and documentation."""
        # Create modification certificate data
        certificate_data = {
            "modification_id": self.name,
            "instrument_profile": self.instrument_profile,
            "instrument_serial": self.instrument_serial,
            "modification_type": self.modification_type,
            "modification_reason": self.modification_reason,
            "authorized_by": self.authorized_by,
            "effective_date": str(self.effective_date),
            "warranty_impact": self.impact_type,
            "new_warranty_period": (
                f"{self.new_warranty_start_date} to {self.new_warranty_end_date}"
                if self.new_warranty_start_date and self.new_warranty_end_date
                else None
            ),
            "issued_date": str(getdate()),
            "issued_by": frappe.session.user,
        }

        # Store certificate data
        self.modification_certificate = json.dumps(certificate_data, indent=2, default=str)

    def _log_modification_audit(self):
        """Log warranty modification for audit compliance."""
        frappe.logger("warranty_modification_audit").info(
            {
                "action": "warranty_modification",
                "instrument_profile": self.instrument_profile,
                "instrument_serial": self.instrument_serial,
                "modification_type": self.modification_type,
                "modification_reason": self.modification_reason,
                "authorized_by": self.authorized_by,
                "effective_date": str(self.effective_date),
                "original_warranty_start": (
                    str(self.original_warranty_start) if self.original_warranty_start else None
                ),
                "original_warranty_end": (
                    str(self.original_warranty_end) if self.original_warranty_end else None
                ),
                "new_warranty_start": (
                    str(self.new_warranty_start_date) if self.new_warranty_start_date else None
                ),
                "new_warranty_end": str(self.new_warranty_end_date) if self.new_warranty_end_date else None,
                "warranty_impact_days": self.warranty_impact_days,
                "cost_impact": self.cost_impact,
                "approval_reference": self.approval_reference,
                "user": frappe.session.user,
                "timestamp": str(self.modification_timestamp),
            }
        )

    @frappe.whitelist()
    def get_modification_history(self):
        """Get modification history for this instrument."""
        if not frappe.has_permission(self.doctype, "read"):
            frappe.throw(_("No permission to view modification history"))

        if not self.instrument_profile:
            return []

        history = frappe.get_all(
            self.doctype,
            filters={"instrument_profile": self.instrument_profile, "docstatus": ["!=", 2]},
            fields=[
                "name",
                "effective_date",
                "modification_type",
                "modification_reason",
                "authorized_by",
                "warranty_impact_days",
                "cost_impact",
            ],
            order_by="effective_date desc",
            limit=20,
        )

        return history

    @frappe.whitelist()
    def calculate_warranty_timeline(self):
        """Calculate complete warranty timeline with all modifications."""
        if not frappe.has_permission(self.doctype, "read"):
            frappe.throw(_("No permission to calculate warranty timeline"))

        if not self.instrument_profile:
            return {}

        # Get all modifications
        modifications = frappe.get_all(
            self.doctype,
            filters={
                "instrument_profile": self.instrument_profile,
                "docstatus": 1,  # Only submitted modifications
            },
            fields=[
                "effective_date",
                "modification_type",
                "warranty_impact_days",
                "new_warranty_start_date",
                "new_warranty_end_date",
            ],
            order_by="effective_date",
        )

        # Build timeline
        timeline = []
        current_start = self.original_warranty_start
        current_end = self.original_warranty_end

        for mod in modifications:
            timeline.append(
                {
                    "date": mod.effective_date,
                    "type": mod.modification_type,
                    "impact_days": mod.warranty_impact_days,
                    "warranty_start": current_start,
                    "warranty_end": current_end,
                }
            )

            # Update current dates if modification specifies new dates
            if mod.new_warranty_start_date:
                current_start = mod.new_warranty_start_date
            if mod.new_warranty_end_date:
                current_end = mod.new_warranty_end_date

        return {
            "original_start": self.original_warranty_start,
            "original_end": self.original_warranty_end,
            "current_start": current_start,
            "current_end": current_end,
            "modifications": timeline,
            "total_modifications": len(modifications),
        }
