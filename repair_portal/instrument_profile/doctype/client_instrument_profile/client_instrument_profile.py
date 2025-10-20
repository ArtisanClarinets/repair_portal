# Path: repair_portal/instrument_profile/doctype/client_instrument_profile/client_instrument_profile.py
# Date: 2025-10-02
# Version: 2.0.0
# Description: Enterprise-grade client-facing instrument profile with comprehensive validation, consent logging, external work history, and technician verification workflow
# Dependencies: frappe, repair_portal.instrument_profile.utils.input_validation, Instrument Serial Number, Customer, Consent Log Entry

import frappe
from frappe import _
from frappe.model.document import Document
from typing import Dict, Any, Optional

from repair_portal.instrument_profile.utils.input_validation import InputValidator, ValidationError

# Security configuration
MAX_NOTES_LENGTH = 2000
MAX_MODEL_LENGTH = 100
ALLOWED_FILE_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"]
MAX_FILE_SIZE_MB = 5


class ClientInstrumentProfile(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from repair_portal.customer.doctype.consent_log_entry.consent_log_entry import (
            ConsentLogEntry,
        )
        from repair_portal.instrument_profile.doctype.customer_external_work_log.customer_external_work_log import (
            CustomerExternalWorkLog,
        )
        from repair_portal.instrument_profile.doctype.instrument_photo.instrument_photo import (
            InstrumentPhoto,
        )

        anonymize_for_research: DF.Check
        condition_images: DF.Table[InstrumentPhoto]
        consent_log: DF.Table[ConsentLogEntry]
        external_work_logs: DF.Table[CustomerExternalWorkLog]
        instrument_category: DF.Literal["Clarinet", "Bass Clarinet", "Contrabass Clarinet"]
        instrument_model: DF.Data
        instrument_owner: DF.Link
        ownership_transfer_to: DF.Link | None
        purchase_receipt: DF.Attach | None
        repair_preferences: DF.SmallText | None
        serial_no: DF.Link
        technician_notes: DF.Text | None
        verification_status: DF.Literal["Pending", "Approved", "Rejected"]

    # end: auto-generated types
    """
    Enterprise-grade client-facing instrument profile with comprehensive security features.
    
    Key Features:
    - Comprehensive input validation and sanitization
    - XSS protection for all text fields
    - Permission-based field access control
    - File upload security validation
    - Audit logging for all changes
    - Cross-reference validation
    """

    def before_insert(self):
        """Pre-insertion validation and security checks"""
        try:
            # Log creation attempt for audit trail
            frappe.logger("client_instrument_profile").info(
                f"Creating new Client Instrument Profile: user={frappe.session.user}, "
                f"serial_no={self.get('serial_no', 'Unknown')}"
            )

            # Validate permissions
            self._validate_create_permissions()

            # Comprehensive input validation
            self._validate_and_sanitize_inputs()

            # Set default values
            self._set_default_values()

        except Exception as e:
            frappe.logger("client_instrument_profile").error(
                f"Failed to create Client Instrument Profile: {str(e)}"
            )
            raise

    def validate(self):
        """Enhanced validation with comprehensive security checks"""
        try:
            # Input validation and sanitization
            self._validate_and_sanitize_inputs()

            # Business rule validation
            self._validate_required_fields()
            self._validate_ownership()
            self._validate_verification()

            # Cross-reference validation
            self._validate_cross_references()

            # File upload validation
            self._validate_file_uploads()

            # Audit log validation changes
            self._log_field_changes()

        except ValidationError as e:
            frappe.logger("client_instrument_profile").warning(
                f"Validation failed for Client Instrument Profile {self.name}: {str(e)}"
            )
            frappe.throw(str(e))
        except Exception as e:
            frappe.logger("client_instrument_profile").error(
                f"Unexpected validation error for Client Instrument Profile {self.name}: {str(e)}"
            )
            frappe.log_error(f"Client Instrument Profile Validation Error: {str(e)}", "Validation Error")
            raise

    def on_update(self):
        """Enhanced update handling with security logging"""
        try:
            # Log update for audit trail
            frappe.logger("client_instrument_profile").info(
                f"Updating Client Instrument Profile {self.name}: user={frappe.session.user}"
            )

            # Handle approval and create instrument profile if needed
            if self.verification_status == "Approved" and self.has_value_changed("verification_status"):
                self._create_or_update_instrument_profile()

        except Exception as e:
            frappe.logger("client_instrument_profile").error(
                f"Update failed for Client Instrument Profile {self.name}: {str(e)}"
            )
            raise

    def on_trash(self):
        """Enhanced deletion with security checks and audit logging"""
        try:
            # Validate delete permissions
            if not frappe.has_permission("Client Instrument Profile", "delete", self.name):
                frappe.throw(_("Insufficient permissions to delete this Client Instrument Profile"))

            # Log deletion for audit trail
            frappe.logger("client_instrument_profile").warning(
                f"Deleting Client Instrument Profile {self.name}: user={frappe.session.user}, "
                f"serial_no={self.get('serial_no', 'Unknown')}"
            )

        except Exception as e:
            frappe.logger("client_instrument_profile").error(
                f"Deletion failed for Client Instrument Profile {self.name}: {str(e)}"
            )
            raise

    def _validate_create_permissions(self):
        """Validate permissions for creating new client instrument profiles"""

        if not frappe.has_permission("Client Instrument Profile", "create"):
            raise ValidationError(_("Insufficient permissions to create Client Instrument Profile"))

        # Additional role-based checks
        allowed_roles = [
            "System Manager",
            "Customer",
            "Portal User",
            "Repair Manager",
        ]

        if not any(frappe.has_role(role=role) for role in allowed_roles):
            raise ValidationError(_("User role not authorized for Client Instrument Profile creation"))

    def _validate_and_sanitize_inputs(self):
        """Comprehensive input validation and sanitization"""

        # Prepare data for validation
        validation_data = {}

        # Core fields validation
        if self.get("serial_no"):
            validation_data["serial_no"] = self.serial_no
        if self.get("instrument_model"):
            validation_data["instrument_model"] = self.instrument_model
        if self.get("instrument_category"):
            validation_data["instrument_category"] = self.instrument_category
        if self.get("instrument_owner"):
            validation_data["instrument_owner"] = self.instrument_owner
        if self.get("ownership_transfer_to"):
            validation_data["ownership_transfer_to"] = self.ownership_transfer_to
        if self.get("verification_status"):
            validation_data["verification_status"] = self.verification_status

        # Text fields that need sanitization
        text_fields = ["repair_preferences", "technician_notes"]
        for field in text_fields:
            value = self.get(field)
            if value:
                validation_data[field] = value

        # Validate using the comprehensive validator
        try:
            validator = InputValidator(strict_mode=True, log_violations=True)

            # Custom schema for this DocType
            schema = self._get_validation_schema()
            filtered_data = {k: v for k, v in validation_data.items() if k in schema}

            if filtered_data:
                validated_data = validator.validate_and_sanitize(filtered_data, schema)

                # Apply sanitized values back
                for field, value in validated_data.items():
                    self.set(field, value)

        except ValidationError as e:
            frappe.throw(f"Input validation failed: {str(e)}")

    def _get_validation_schema(self) -> Dict[str, Dict[str, Any]]:
        """Get validation schema for this DocType"""

        return {
            "serial_no": {"type": "link", "target_doctype": "Instrument Serial Number", "required": True},
            "instrument_model": {
                "type": "string",
                "required": True,
                "max_length": MAX_MODEL_LENGTH,
                "sanitize": True,
            },
            "instrument_category": {
                "type": "select",
                "options": ["Clarinet", "Bass Clarinet", "Contrabass Clarinet"],
                "required": True,
            },
            "instrument_owner": {"type": "link", "target_doctype": "Customer", "required": True},
            "ownership_transfer_to": {"type": "link", "target_doctype": "Customer", "required": False},
            "verification_status": {
                "type": "select",
                "options": ["Pending", "Approved", "Rejected"],
                "required": False,
            },
            "repair_preferences": {
                "type": "string",
                "required": False,
                "max_length": MAX_NOTES_LENGTH,
                "sanitize": True,
            },
            "technician_notes": {
                "type": "string",
                "required": False,
                "max_length": MAX_NOTES_LENGTH,
                "sanitize": True,
            },
        }

    def _validate_required_fields(self):
        """Ensure required fields are present with enhanced validation"""
        if not self.instrument_owner:
            raise ValidationError(_("Instrument Owner is required"))
        if not self.instrument_model:
            raise ValidationError(_("Instrument Model is required"))
        if not self.serial_no:
            raise ValidationError(_("Serial Number is required"))
        if not self.instrument_category:
            raise ValidationError(_("Instrument Category is required"))

    def _validate_ownership(self):
        """Validate ownership transfer logic with enhanced security checks"""
        if self.ownership_transfer_to:
            if self.ownership_transfer_to == self.instrument_owner:
                raise ValidationError(_("Cannot transfer ownership to the same owner"))

            # Validate customer exists and user has permission
            if not frappe.db.exists("Customer", self.ownership_transfer_to):
                raise ValidationError(_("Transfer target customer does not exist"))

            if not frappe.has_permission("Customer", "read", self.ownership_transfer_to):
                raise ValidationError(_("Invalid customer for ownership transfer"))

    def _validate_verification(self):
        """Validate verification status transitions with enhanced security"""
        if self.verification_status == "Rejected" and not self.technician_notes:
            raise ValidationError(_("Technician Notes required when rejecting instrument"))

        # Only authorized users can change verification status
        if self.has_value_changed("verification_status"):
            authorized_roles = ["Technician", "Repair Manager", "System Manager"]

            if not any(frappe.has_role(role=role) for role in authorized_roles):
                raise ValidationError(_("Only technicians can change verification status"))

            # Log verification status changes
            frappe.logger("client_instrument_profile_audit").info(
                f"Verification status changed for {self.name}: "
                f"{self.get_db_value('verification_status')} -> {self.verification_status} "
                f"by {frappe.session.user}"
            )

    def _validate_cross_references(self):
        """Validate cross-references and data consistency"""

        # Validate serial number link
        if self.get("serial_no") and not frappe.db.exists("Instrument Serial Number", self.serial_no):
            raise ValidationError(f"Invalid serial number reference: {self.serial_no}")

        # Validate instrument owner
        if self.get("instrument_owner"):
            if not frappe.db.exists("Customer", self.instrument_owner):
                raise ValidationError(f"Invalid instrument owner reference: {self.instrument_owner}")

            # Check customer permissions
            if not frappe.has_permission("Customer", "read", self.instrument_owner):
                raise ValidationError("Insufficient permissions for specified instrument owner")

    def _validate_file_uploads(self):
        """Validate file uploads for security"""

        # Validate purchase receipt
        if self.get("purchase_receipt"):
            self._validate_file(self.purchase_receipt, "purchase_receipt")

        # Validate condition images
        condition_images = self.get("condition_images", [])
        for i, image in enumerate(condition_images):
            if image.get("photo"):
                self._validate_file(image.photo, f"condition_images[{i}].photo")

    def _validate_file(self, file_url: str, field_name: str):
        """Validate individual file for security"""

        if not file_url:
            return

        try:
            # Get file document
            file_doc = frappe.get_doc("File", {"file_url": file_url})

            # Validate file extension
            file_extension = file_doc.get_extension().lower()
            if file_extension not in ALLOWED_FILE_EXTENSIONS:
                raise ValidationError(
                    f"Invalid file type for {field_name}. Allowed types: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
                )

            # Validate file size
            if file_doc.file_size and file_doc.file_size > (MAX_FILE_SIZE_MB * 1024 * 1024):
                raise ValidationError(f"File size for {field_name} exceeds {MAX_FILE_SIZE_MB}MB limit")

        except frappe.DoesNotExistError:
            raise ValidationError(f"File not found for {field_name}")

    def _set_default_values(self):
        """Set secure default values for new records"""

        if not self.get("verification_status"):
            self.verification_status = "Pending"

    def _log_field_changes(self):
        """Log field changes for audit trail"""

        if self.is_new():
            return

        changed_fields = self.get_dirty_fields()
        if not changed_fields:
            return

        # Log significant field changes
        significant_fields = [
            "instrument_owner",
            "verification_status",
            "ownership_transfer_to",
            "instrument_category",
            "instrument_model",
        ]

        significant_changes = {
            field: {"old": self.get_db_value(field), "new": self.get(field)}
            for field in changed_fields
            if field in significant_fields
        }

        if significant_changes:
            frappe.logger("client_instrument_profile_audit").info(
                f"Field changes for Client Instrument Profile {self.name}: "
                f"user={frappe.session.user}, changes={significant_changes}"
            )

    def _create_or_update_instrument_profile(self):
        """Create or update Instrument Profile when approved with enhanced security"""
        try:
            # Verify approval permissions
            if not frappe.has_permission("Instrument Profile", "create"):
                raise ValidationError(_("Insufficient permissions to create Instrument Profile"))

            # Check if instrument exists
            instrument = frappe.db.get_value("Instrument", {"serial_no": self.serial_no}, "name")

            if not instrument:
                # Create new Instrument first with validation
                instrument_doc = frappe.get_doc(
                    {
                        "doctype": "Instrument",
                        "serial_no": self.serial_no,
                        "customer": self.instrument_owner,
                        "instrument_type": self.instrument_category,
                        "model": self.instrument_model,
                    }
                )
                instrument_doc.insert(ignore_permissions=True)
                instrument = instrument_doc.name

                frappe.logger("client_instrument_profile").info(
                    f"Created new Instrument {instrument} from Client Profile {self.name}"
                )

            # Check if profile exists
            profile = frappe.db.get_value("Instrument Profile", {"instrument": instrument}, "name")

            if not profile:
                # Create new profile with validation
                profile_doc = frappe.get_doc(
                    {
                        "doctype": "Instrument Profile",
                        "instrument": instrument,
                        "customer": self.instrument_owner,
                        "initial_condition_notes": self.repair_preferences or "",
                    }
                )
                profile_doc.insert(ignore_permissions=True)

                frappe.logger("client_instrument_profile").info(
                    f"Created new Instrument Profile {profile_doc.name} from Client Profile {self.name}"
                )

                frappe.msgprint(
                    _("Instrument Profile {0} created").format(profile_doc.name),
                    alert=True,
                    indicator="green",
                )
            else:
                frappe.logger("client_instrument_profile").info(
                    f"Instrument Profile {profile} already exists for Client Profile {self.name}"
                )

        except Exception as e:
            frappe.logger("client_instrument_profile").error(
                f"Failed to create Instrument Profile from Client Profile {self.name}: {str(e)}"
            )
            frappe.log_error(
                frappe.get_traceback(), "Client Instrument Profile: Failed to create Instrument Profile"
            )
            frappe.throw(_("Failed to create Instrument Profile: {0}").format(str(e)))
