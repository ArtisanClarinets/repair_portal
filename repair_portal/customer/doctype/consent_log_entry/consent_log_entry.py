# Path: repair_portal/repair_portal/customer/doctype/consent_log_entry/consent_log_entry.py
# Date: 2025-01-27
# Version: 3.1.0
# Description: Child table for consent log entries with comprehensive validation, audit trail management, and automatic status tracking
# Dependencies: frappe.model.document, frappe.utils

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, format_datetime, getdate, now_datetime


class ConsentLogEntry(Document):
    """Child table for Consent Log Entry with comprehensive logging and status management."""

    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        entry_date: DF.Date
        method: DF.Select
        technician: DF.Link
        notes: DF.SmallText
        consent_type: DF.Select
        date_given: DF.Date
        reference_doctype: DF.Link
        reference_name: DF.DynamicLink
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
    # end: auto-generated types

    def validate(self) -> None:
        """Comprehensive validation for consent log entry."""
        self._validate_required_fields()
        self._validate_dates()
        self._validate_references()
        self._validate_consent_logic()
        self._set_defaults()

    def _validate_required_fields(self) -> None:
        """Validate essential fields are present."""
        if not self.entry_date:
            frappe.throw(_("Entry Date is required"))

        if not self.method:
            frappe.throw(_("Method is required"))

        if not self.consent_type:
            frappe.throw(_("Consent Type is required"))

    def _validate_dates(self) -> None:
        """Validate date logic and constraints."""
        # Entry date should not be in the future
        if self.entry_date and getdate(self.entry_date) > getdate():
            frappe.throw(_("Entry Date cannot be in the future"))

        # Date given should not be in the future
        if self.date_given and getdate(self.date_given) > getdate():
            frappe.throw(_("Date Given cannot be in the future"))

        # Date given should not be before entry date
        if self.entry_date and self.date_given:
            if getdate(self.date_given) > getdate(self.entry_date):
                frappe.throw(_("Date Given cannot be after Entry Date"))

    def _validate_references(self) -> None:
        """Validate reference document consistency."""
        # If reference doctype is specified, reference name should also be specified
        if self.reference_doctype and not self.reference_name:
            frappe.throw(_("Reference Name is required when Reference DocType is specified"))

        # If reference name is specified, reference doctype should also be specified
        if self.reference_name and not self.reference_doctype:
            frappe.throw(_("Reference DocType is required when Reference Name is specified"))

        # Validate that referenced document exists
        if self.reference_doctype and self.reference_name:
            if not frappe.db.exists(self.reference_doctype, self.reference_name):
                frappe.throw(
                    _("Referenced document {0} {1} does not exist").format(
                        self.reference_doctype, self.reference_name
                    )
                )

    def _validate_consent_logic(self) -> None:
        """Validate consent-specific business logic."""
        # Validate method is appropriate for consent type
        valid_methods = {
            "Repair Authorization": ["Phone", "Email", "In Person"],
            "Photography": ["In Person", "Email"],
            "Privacy Waiver": ["In Person", "Email"],
        }

        if self.consent_type in valid_methods:
            if self.method not in valid_methods[self.consent_type]:
                frappe.msgprint(
                    _("Warning: {0} method is unusual for {1} consent type").format(
                        self.method, self.consent_type
                    ),
                    alert=True,
                )

        # Validate technician exists
        if self.technician and not frappe.db.exists("User", self.technician):
            frappe.throw(_("Technician {0} does not exist").format(self.technician))

    def _set_defaults(self) -> None:
        """Set default values for various fields."""
        # Default entry date to today
        if not self.entry_date:
            self.entry_date = getdate()

        # Default date given to entry date if not specified
        if not self.date_given and self.entry_date:
            self.date_given = self.entry_date

        # Default technician to current user if not specified
        if not self.technician:
            self.technician = frappe.session.user

    def get_consent_status(self) -> str:
        """Determine current consent status based on entry data."""
        if not self.date_given:
            return "Pending"

        # Check if consent is still valid (basic logic)
        if self.consent_type == "Repair Authorization":
            # Repair authorization valid for 1 year
            expiry_date = add_days(self.date_given, 365)
            if getdate() > getdate(expiry_date):
                return "Expired"
            return "Active"

        elif self.consent_type in ["Photography", "Privacy Waiver"]:
            # Photography and privacy waivers are generally permanent unless revoked
            return "Active"

        return "Unknown"

    def get_consent_validity(self) -> dict[str, Any]:
        """Get detailed consent validity information."""
        validity = {
            "status": self.get_consent_status(),
            "date_given": self.date_given,
            "expires_on": None,
            "days_remaining": None,
            "is_valid": False,
        }

        if not self.date_given:
            return validity

        # Calculate expiry based on consent type
        if self.consent_type == "Repair Authorization":
            expiry_date = add_days(self.date_given, 365)
            validity["expires_on"] = expiry_date

            if getdate() <= getdate(expiry_date):
                validity["is_valid"] = True
                validity["days_remaining"] = (getdate(expiry_date) - getdate()).days

        elif self.consent_type in ["Photography", "Privacy Waiver"]:
            # These are generally permanent
            validity["is_valid"] = True
            validity["expires_on"] = None

        return validity

    def create_audit_entry(self, action: str, details: str | None = None) -> None:
        """Create audit trail entry for consent actions."""
        try:
            {
                "doctype": "Consent Log Entry",
                "entry_date": getdate(),
                "method": "System",
                "technician": frappe.session.user,
                "consent_type": self.consent_type,
                "date_given": self.date_given,
                "notes": f"Audit: {action}. {details or ''}".strip(),
                "reference_doctype": self.reference_doctype,
                "reference_name": self.reference_name,
                "parent": self.parent,
                "parenttype": self.parenttype,
                "parentfield": self.parentfield,
            }

            frappe.log_error(
                f"Consent audit: {action} for {self.consent_type}", f"consent_audit_{self.parent}"
            )

        except Exception as e:
            frappe.log_error(f"Failed to create audit entry: {str(e)}")

    def confirm_consent(self, confirmed_by: str | None = None, notes: str | None = None) -> dict[str, Any]:
        """Confirm consent and update status."""
        result = {"success": False, "message": "", "status": None}

        try:
            # Update confirmation details
            if not self.date_given:
                self.date_given = getdate()

            if confirmed_by:
                self.technician = confirmed_by

            if notes:
                self.notes = f"{self.notes or ''}\nConfirmed: {notes}".strip()

            # Create audit trail
            self.create_audit_entry(
                "Consent Confirmed", f"Confirmed by {confirmed_by or frappe.session.user}"
            )

            result["success"] = True
            result["message"] = "Consent confirmed successfully"
            result["status"] = self.get_consent_status()

        except Exception as e:
            result["message"] = f"Failed to confirm consent: {str(e)}"

        return result

    def revoke_consent(self, revoked_by: str | None = None, reason: str | None = None) -> dict[str, Any]:
        """Revoke consent and update status."""
        result = {"success": False, "message": "", "status": None}

        try:
            # Add revocation note
            revocation_note = (
                f"REVOKED on {format_datetime(now_datetime())} by {revoked_by or frappe.session.user}"
            )
            if reason:
                revocation_note += f". Reason: {reason}"

            self.notes = f"{self.notes or ''}\n{revocation_note}".strip()

            # Create audit trail
            self.create_audit_entry(
                "Consent Revoked",
                f"Revoked by {revoked_by or frappe.session.user}. Reason: {reason or 'Not specified'}",
            )

            result["success"] = True
            result["message"] = "Consent revoked successfully"
            result["status"] = "Revoked"

        except Exception as e:
            result["message"] = f"Failed to revoke consent: {str(e)}"

        return result

    @staticmethod
    def get_active_consents(customer: str, consent_type: str | None = None) -> list[dict[str, Any]]:
        """Get all active consents for a customer."""
        filters = {"parent": customer, "parenttype": "Customer"}

        if consent_type:
            filters["consent_type"] = consent_type

        consents = frappe.get_all(
            "Consent Log Entry", filters=filters, fields=["*"], order_by="date_given desc"
        )

        # Filter for active consents only
        active_consents = []
        for consent_data in consents:
            consent = frappe.get_doc("Consent Log Entry", consent_data.name)
            validity = consent.get_consent_validity()
            if validity["is_valid"]:
                consent_data.update(validity)
                active_consents.append(consent_data)

        return active_consents

    @staticmethod
    def check_consent_coverage(customer: str, required_types: list[str]) -> dict[str, Any]:
        """Check if customer has all required consent types."""
        coverage = {"complete": True, "missing": [], "expired": [], "details": {}}

        for consent_type in required_types:
            active_consents = ConsentLogEntry.get_active_consents(customer, consent_type)

            if not active_consents:
                coverage["complete"] = False
                coverage["missing"].append(consent_type)
                coverage["details"][consent_type] = {"status": "missing"}
            else:
                # Get the most recent consent
                latest_consent = active_consents[0]
                coverage["details"][consent_type] = latest_consent

                if latest_consent.get("status") == "Expired":
                    coverage["complete"] = False
                    coverage["expired"].append(consent_type)

        return coverage
