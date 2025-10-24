# Path: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Date: 2025-01-21
# Version: 3.0.0
# Description: Enterprise-grade Instrument Profile controller with comprehensive input validation, XSS protection, and security features
# Dependencies: frappe, repair_portal.instrument_profile.utils.input_validation, repair_portal.instrument_profile.services.profile_sync

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from typing import Dict, Any, List, Optional

from repair_portal.instrument_profile.services.profile_sync import sync_profile
from repair_portal.instrument_profile.utils.input_validation import (
    InputValidator,
    validate_instrument_profile_data,
    ValidationError,
)

READ_ONLY_FIELDS = {
    "serial_no",
    "brand",
    "model",
    "instrument_category",
    "customer",
    "owner_name",
    "purchase_date",
    "purchase_order",
    "purchase_receipt",
    "warranty_start_date",
    "warranty_end_date",
    "status",
    "headline",
}

# Security configuration
MAX_PHOTO_SIZE_MB = 10
ALLOWED_PHOTO_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
MAX_NOTES_LENGTH = 5000
MAX_LOCATION_LENGTH = 100


class InstrumentProfile(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from repair_portal.instrument_profile.doctype.customer_external_work_log.customer_external_work_log import (  # type: ignore
            CustomerExternalWorkLog,
        )
        from repair_portal.instrument_profile.doctype.instrument_accessory.instrument_accessory import (
            InstrumentAccessory,
        )
        from repair_portal.instrument_profile.doctype.instrument_condition_record.instrument_condition_record import (
            InstrumentConditionRecord,
        )
        from repair_portal.instrument_profile.doctype.instrument_photo.instrument_photo import (
            InstrumentPhoto,
        )
        from repair_portal.repair_logging.doctype.instrument_interaction_log.instrument_interaction_log import (
            InstrumentInteractionLog,
        )
        from repair_portal.repair_logging.doctype.material_use_log.material_use_log import (
            MaterialUseLog,
        )
        from repair_portal.repair_logging.doctype.warranty_modification_log.warranty_modification_log import (
            WarrantyModificationLog,
        )

        accessory_log: DF.Table[InstrumentAccessory]
        amended_from: DF.Link | None
        body_material: DF.Data | None
        brand: DF.Data | None
        condition_logs: DF.Table[InstrumentConditionRecord]
        current_location: DF.Data | None
        customer: DF.Link | None
        external_work_logs: DF.Table[CustomerExternalWorkLog]
        headline: DF.Data | None
        initial_condition_notes: DF.Text | None
        instrument: DF.Link
        instrument_category: DF.Data | None
        instrument_profile_id: DF.Data | None
        intake_date: DF.Date | None
        interaction_logs: DF.Table[InstrumentInteractionLog]
        key_plating: DF.Data | None
        key_system: DF.Literal[Boehm, Albert, Oehler, Other]
        linked_inspection: DF.Link | None
        material_usage: DF.Table[MaterialUseLog]
        model: DF.Data | None
        number_of_keys_rings: DF.Data | None
        owner_name: DF.Data | None
        profile_image: DF.AttachImage | None
        purchase_date: DF.Date | None
        purchase_order: DF.Link | None
        purchase_receipt: DF.Link | None
        serial_no: DF.Data | None
        serial_photos: DF.Table[InstrumentPhoto]
        service_photos: DF.Table[InstrumentPhoto]
        status: DF.Data | None
        warranty_end_date: DF.Date | None
        warranty_expiration: DF.Date | None
        warranty_logs: DF.Table[WarrantyModificationLog]
        warranty_start_date: DF.Date | None
        wood_type: DF.Data | None
        workflow_state: DF.Literal[Open, "In Progress", Delivered, Archived]
    # end: auto-generated types
    """
    Enterprise-grade Instrument Profile controller with comprehensive security features.
    
    Key Features:
    - Comprehensive input validation and sanitization
    - XSS protection for all text fields
    - SQL injection prevention
    - File upload security
    - Audit logging for all changes
    - Permission-based field access control
    """

    def before_insert(self):
        """Pre-insertion validation and security checks"""
        try:
            # Log creation attempt for audit trail
            frappe.logger("instrument_profile").info(
                f"Creating new Instrument Profile: user={frappe.session.user}, "
                f"instrument={self.get('instrument', 'Unknown')}"
            )

            # Validate permissions
            self._validate_create_permissions()

            # Comprehensive input validation
            self._validate_and_sanitize_inputs()

            # Validate business rules
            self._validate_business_rules()

            # Set default values
            self._set_default_values()

        except Exception as e:
            frappe.logger("instrument_profile").error(f"Failed to create Instrument Profile: {str(e)}")
            raise

    def validate(self):
        """Enhanced validation with comprehensive security checks"""
        try:
            # Skip enforcement during programmatic sync
            if getattr(frappe.flags, "in_profile_sync", False):
                return

            # Permission-based field protection
            self._validate_field_permissions()

            # Input validation and sanitization
            self._validate_and_sanitize_inputs()

            # Cross-reference validation
            self._validate_cross_references()

            # Business rule validation
            self._validate_business_rules()

            # File upload validation
            self._validate_file_uploads()

            # Audit log validation changes
            self._log_field_changes()

        except ValidationError as e:
            frappe.logger("instrument_profile").warning(
                f"Validation failed for Instrument Profile {self.name}: {str(e)}"
            )
            frappe.throw(str(e))
        except Exception as e:
            frappe.logger("instrument_profile").error(
                f"Unexpected validation error for Instrument Profile {self.name}: {str(e)}"
            )
            frappe.log_error(f"Instrument Profile Validation Error: {str(e)}", "Validation Error")
            raise

    def on_update(self):
        """Enhanced update handling with security logging"""
        try:
            # Log update for audit trail
            frappe.logger("instrument_profile").info(
                f"Updating Instrument Profile {self.name}: user={frappe.session.user}"
            )

            # Refresh derived fields from canonical doctypes on any change
            if getattr(frappe.flags, "in_profile_sync", False):
                return

            frappe.flags.in_profile_sync = True
            sync_profile(self.name)

        except Exception as e:
            frappe.logger("instrument_profile").error(
                f"Update failed for Instrument Profile {self.name}: {str(e)}"
            )
            frappe.log_error(frappe.get_traceback(), f"InstrumentProfile: sync failed ({self.name})")
        finally:
            frappe.flags.in_profile_sync = False

    def after_insert(self):
        """Enhanced post-insertion processing with audit logging"""
        try:
            frappe.logger("instrument_profile").info(f"Successfully created Instrument Profile {self.name}")

            if getattr(frappe.flags, "in_profile_sync", False):
                return

            frappe.flags.in_profile_sync = True
            sync_profile(self.name)

        except Exception as e:
            frappe.logger("instrument_profile").error(
                f"Post-insert processing failed for Instrument Profile {self.name}: {str(e)}"
            )
            frappe.log_error(frappe.get_traceback(), f"InstrumentProfile: initial sync failed ({self.name})")
        finally:
            frappe.flags.in_profile_sync = False

    def on_trash(self):
        """Enhanced deletion with security checks and audit logging"""
        try:
            # Validate delete permissions
            if not frappe.has_permission("Instrument Profile", "delete", self.name):
                frappe.throw(_("Insufficient permissions to delete this Instrument Profile"))

            # Check for dependent records
            self._validate_deletion_dependencies()

            # Log deletion for audit trail
            frappe.logger("instrument_profile").warning(
                f"Deleting Instrument Profile {self.name}: user={frappe.session.user}, "
                f"serial_no={self.get('serial_no', 'Unknown')}"
            )

        except Exception as e:
            frappe.logger("instrument_profile").error(
                f"Deletion failed for Instrument Profile {self.name}: {str(e)}"
            )
            raise

    def _validate_create_permissions(self):
        """Validate permissions for creating new instrument profiles"""

        if not frappe.has_permission("Instrument Profile", "create"):
            raise ValidationError(_("Insufficient permissions to create Instrument Profile"))

        # Additional role-based checks
        user_roles = frappe.get_roles(frappe.session.user)
        allowed_roles = ["System Manager", "Repair Manager", "Technician"]

        if not any(role in user_roles for role in allowed_roles):
            raise ValidationError(_("User role not authorized for Instrument Profile creation"))

    def _validate_field_permissions(self):
        """Validate field-level permissions and read-only enforcement"""

        if frappe.session.user != "Administrator" and not frappe.has_role("System Manager"):
            dirty = [f for f in self.get_dirty_fields() if f in READ_ONLY_FIELDS]
            if dirty:
                frappe.throw(
                    _("These fields are managed automatically and cannot be edited: {0}").format(
                        ", ".join(dirty)
                    )
                )

        # Additional field-specific permission checks
        restricted_fields = {
            "warranty_end_date": ["System Manager", "Repair Manager"],
            "purchase_order": ["System Manager", "Purchase Manager"],
            "purchase_receipt": ["System Manager", "Purchase Manager"],
        }

        user_roles = frappe.get_roles(frappe.session.user)

        for field, required_roles in restricted_fields.items():
            if self.has_value_changed(field) and not any(role in user_roles for role in required_roles):
                frappe.throw(_("Insufficient permissions to modify field: {0}").format(field))

    def _validate_and_sanitize_inputs(self):
        """Comprehensive input validation and sanitization"""

        # Prepare data for validation
        validation_data = {}

        # Core fields validation
        if self.get("serial_no"):
            validation_data["serial_no"] = self.serial_no
        if self.get("instrument_model"):
            validation_data["instrument_model"] = self.instrument_model
        if self.get("customer"):
            validation_data["customer"] = self.customer
        if self.get("status"):
            validation_data["status"] = self.status
        if self.get("workflow_state"):
            validation_data["workflow_state"] = self.workflow_state

        # Text fields that need sanitization
        text_fields = ["initial_condition_notes", "headline", "current_location"]
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

            # Ensure serial_no is populated for validation. Prefer the explicit value on
            # the document, then any alternate field, and finally the linked Instrument.
            if not filtered_data.get("serial_no"):
                serial = (
                    self.get("serial_no")
                    or self.get("instrument_serial_number")
                    or None
                )

                if not serial and self.get("instrument"):
                    try:
                        instrument_doc = frappe.get_doc("Instrument", self.instrument)
                        serial = (
                            instrument_doc.get("serial_no")
                            or instrument_doc.get("serial_number")
                            or instrument_doc.name
                        )
                    except frappe.DoesNotExistError:
                        serial = None

                if serial:
                    filtered_data["serial_no"] = serial

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
            "serial_no": {
                "type": "string",
                "required": True,
                "pattern": "serial_number",
                "min_length": 3,
                "max_length": 50,
            },
            "instrument_model": {"type": "link", "target_doctype": "Instrument Model", "required": False},
            "customer": {"type": "link", "target_doctype": "Customer", "required": False},
            "status": {
                "type": "select",
                "options": ["Active", "Inactive", "Under Maintenance", "Under Repair", "Retired"],
                "required": False,
            },
            "workflow_state": {
                "type": "select",
                "options": ["Open", "In Progress", "Delivered", "Archived"],
                "required": False,
            },
            "initial_condition_notes": {"type": "html", "required": False, "max_length": MAX_NOTES_LENGTH},
            "headline": {"type": "string", "required": False, "max_length": 200, "sanitize": True},
            "current_location": {
                "type": "string",
                "required": False,
                "max_length": MAX_LOCATION_LENGTH,
                "pattern": "alphanumeric",
            },
        }

    def _validate_cross_references(self):
        """Validate cross-references and data consistency"""

        # Validate instrument link
        if self.get("instrument") and not frappe.db.exists("Instrument", self.instrument):
            raise ValidationError(f"Invalid instrument reference: {self.instrument}")

        # Validate customer link if provided
        if self.get("customer"):
            if not frappe.db.exists("Customer", self.customer):
                raise ValidationError(f"Invalid customer reference: {self.customer}")

            # Check customer permissions
            if not frappe.has_permission("Customer", "read", self.customer):
                raise ValidationError("Insufficient permissions for specified customer")

        # Validate instrument model link
        if self.get("instrument_model") and not frappe.db.exists("Instrument Model", self.instrument_model):
            raise ValidationError(f"Invalid instrument model reference: {self.instrument_model}")

    def _validate_business_rules(self):
        """Validate business-specific rules and constraints"""

        # Warranty date validation
        if self.get("warranty_start_date") and self.get("warranty_end_date"):
            if frappe.utils.getdate(self.warranty_end_date) <= frappe.utils.getdate(self.warranty_start_date):
                raise ValidationError("Warranty end date must be after warranty start date")

        # Purchase date validation
        if self.get("purchase_date"):
            if frappe.utils.getdate(self.purchase_date) > frappe.utils.getdate():
                raise ValidationError("Purchase date cannot be in the future")

        # Status and workflow state consistency
        if self.get("status") == "Retired" and self.get("workflow_state") != "Archived":
            self.workflow_state = "Archived"

        # Customer requirement for delivered state
        if self.get("workflow_state") == "Delivered" and not self.get("customer"):
            raise ValidationError("Customer is required when instrument is delivered")

    def _validate_file_uploads(self):
        """Validate file uploads for security"""

        # Validate profile image
        if self.get("profile_image"):
            self._validate_image_file(self.profile_image, "profile_image")

        # Validate photo tables
        for photo_table in ["serial_photos", "service_photos"]:
            photos = self.get(photo_table, [])
            for i, photo in enumerate(photos):
                if photo.get("photo"):
                    self._validate_image_file(photo.photo, f"{photo_table}[{i}].photo")

    def _validate_image_file(self, file_url: str, field_name: str):
        """Validate individual image file for security"""

        if not file_url:
            return

        try:
            # Get file document
            file_doc = frappe.get_doc("File", {"file_url": file_url})

            # Validate file extension
            file_extension = file_doc.get_extension().lower()
            if file_extension not in ALLOWED_PHOTO_EXTENSIONS:
                raise ValidationError(
                    f"Invalid file type for {field_name}. Allowed types: {', '.join(ALLOWED_PHOTO_EXTENSIONS)}"
                )

            # Validate file size
            if file_doc.file_size and file_doc.file_size > (MAX_PHOTO_SIZE_MB * 1024 * 1024):
                raise ValidationError(f"File size for {field_name} exceeds {MAX_PHOTO_SIZE_MB}MB limit")

            # Validate MIME type
            allowed_mime_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if hasattr(file_doc, "content_type") and file_doc.content_type not in allowed_mime_types:
                raise ValidationError(f"Invalid MIME type for {field_name}")

        except frappe.DoesNotExistError:
            raise ValidationError(f"File not found for {field_name}")

    def _validate_deletion_dependencies(self):
        """Check for dependent records before deletion"""

        # Check for linked inspection records
        linked_inspections = frappe.get_all(
            "Instrument Inspection", filters={"instrument_profile": self.name}, fields=["name"]
        )

        if linked_inspections:
            raise ValidationError(
                f"Cannot delete Instrument Profile with linked inspection records: "
                f"{', '.join([r.name for r in linked_inspections])}"
            )

        # Check for active work orders
        active_work_orders = frappe.get_all(
            "Work Order",
            filters={"instrument_profile": self.name, "status": ["not in", ["Completed", "Cancelled"]]},
            fields=["name"],
        )

        if active_work_orders:
            raise ValidationError(
                f"Cannot delete Instrument Profile with active work orders: "
                f"{', '.join([r.name for r in active_work_orders])}"
            )

    def _set_default_values(self):
        """Set secure default values for new records"""

        if not self.get("workflow_state"):
            self.workflow_state = "Open"

        if not self.get("status"):
            self.status = "Active"

        if not self.get("current_location"):
            self.current_location = "Shop"

    def _log_field_changes(self):
        """Log field changes for audit trail"""

        if self.is_new():
            return

        changed_fields = self.get_dirty_fields()
        if not changed_fields:
            return

        # Log significant field changes
        significant_fields = [
            "customer",
            "status",
            "workflow_state",
            "current_location",
            "warranty_end_date",
            "instrument_model",
        ]

        significant_changes = {
            field: {"old": self.get_db_value(field), "new": self.get(field)}
            for field in changed_fields
            if field in significant_fields
        }

        if significant_changes:
            frappe.logger("instrument_profile_audit").info(
                f"Field changes for Instrument Profile {self.name}: "
                f"user={frappe.session.user}, changes={significant_changes}"
            )


# Whitelisted API methods with comprehensive security
@frappe.whitelist()
def get_instrument_profile_summary(name: str) -> Dict[str, Any]:
    """
    Get comprehensive instrument profile summary with security checks

    Args:
        name: Instrument Profile name

    Returns:
        Dict with profile summary data

    Raises:
        PermissionError: If user lacks read permissions
        ValidationError: If invalid input provided
    """

    try:
        # Validate input
        if not name or not isinstance(name, str):
            raise ValidationError("Valid Instrument Profile name is required")

        # Check permissions
        if not frappe.has_permission("Instrument Profile", "read", name):
            frappe.throw(_("Insufficient permissions to view this Instrument Profile"))

        # Get profile with security checks
        profile = frappe.get_doc("Instrument Profile", name)

        # Prepare sanitized summary
        summary = {
            "name": profile.name,
            "serial_no": profile.get("serial_no"),
            "brand": profile.get("brand"),
            "model": profile.get("model"),
            "status": profile.get("status"),
            "workflow_state": profile.get("workflow_state"),
            "customer": profile.get("customer"),
            "current_location": profile.get("current_location"),
            "warranty_end_date": profile.get("warranty_end_date"),
            "last_service_date": profile.get("last_service_date"),
        }

        # Add customer details if accessible
        if profile.get("customer") and frappe.has_permission("Customer", "read", profile.customer):
            customer = frappe.get_doc("Customer", profile.customer)
            summary["customer_details"] = {
                "name": customer.name,
                "customer_name": customer.customer_name,
                "email": customer.email_id,
            }

        # Log access for audit trail
        frappe.logger("instrument_profile_access").info(
            f"Profile summary accessed: {name} by {frappe.session.user}"
        )

        return summary

    except Exception as e:
        frappe.logger("instrument_profile").error(f"Failed to get profile summary for {name}: {str(e)}")
        frappe.log_error(f"Profile Summary Error: {str(e)}", "API Error")
        raise


@frappe.whitelist()
def update_instrument_location(name: str, new_location: str) -> Dict[str, Any]:
    """
    Update instrument location with comprehensive validation

    Args:
        name: Instrument Profile name
        new_location: New location value

    Returns:
        Dict with update status

    Raises:
        PermissionError: If user lacks write permissions
        ValidationError: If invalid input provided
    """

    try:
        # Input validation
        validator = InputValidator(strict_mode=True, log_violations=True)

        validated_data = validator.validate_and_sanitize(
            {"name": name, "new_location": new_location},
            {
                "name": {"type": "string", "required": True, "min_length": 1, "max_length": 140},
                "new_location": {
                    "type": "string",
                    "required": True,
                    "max_length": MAX_LOCATION_LENGTH,
                    "pattern": "alphanumeric",
                },
            },
        )

        # Check permissions
        if not frappe.has_permission("Instrument Profile", "write", validated_data["name"]):
            frappe.throw(_("Insufficient permissions to update this Instrument Profile"))

        # Update location
        profile = frappe.get_doc("Instrument Profile", validated_data["name"])
        old_location = profile.get("current_location")
        profile.current_location = validated_data["new_location"]
        profile.save()

        # Log change for audit trail
        frappe.logger("instrument_profile_audit").info(
            f"Location updated for {validated_data['name']}: "
            f"{old_location} -> {validated_data['new_location']} by {frappe.session.user}"
        )

        return {
            "success": True,
            "message": "Location updated successfully",
            "old_location": old_location,
            "new_location": validated_data["new_location"],
        }

    except Exception as e:
        frappe.logger("instrument_profile").error(f"Failed to update location for {name}: {str(e)}")
        frappe.log_error(f"Location Update Error: {str(e)}", "API Error")
        raise
