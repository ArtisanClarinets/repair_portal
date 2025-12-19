# Path: repair_portal/instrument_profile/doctype/customer_external_work_log/customer_external_work_log.py
# Date: 2025-10-02
# Version: 2.0.0
# Description: Enterprise-grade child table controller for customer-submitted external work logs with comprehensive validation and security
# Dependencies: frappe, repair_portal.instrument_profile.utils.input_validation

import frappe
from frappe import _
from frappe.model.document import Document
from typing import Dict, Any

from repair_portal.instrument_profile.utils.input_validation import InputValidator, ValidationError

# Security configuration
MAX_SHOP_NAME_LENGTH = 200
MAX_NOTES_LENGTH = 1000
ALLOWED_FILE_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"]
MAX_FILE_SIZE_MB = 3


class CustomerExternalWorkLog(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        external_shop_name: DF.Data | None
        instrument: DF.Link
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        receipt_attachment: DF.Attach | None
        service_date: DF.Date
        service_notes: DF.Text | None
        service_type: DF.Literal["Inspection", "Setup", "Maintenance", "Repair", "Other"]
    # end: auto-generated types
    """
    Enterprise-grade external work log with comprehensive validation and security.
    
    Key Features:
    - Input validation and sanitization for all fields
    - XSS protection for text content
    - File upload security validation
    - Business rule enforcement
    - Audit logging integration
    """

    def validate(self):
        """Enhanced validation with comprehensive security checks"""
        try:
            # Input validation and sanitization
            self._validate_and_sanitize_inputs()

            # Business rule validation
            self._validate_required_fields()
            self._validate_business_rules()

            # Cross-reference validation
            self._validate_cross_references()

            # File upload validation
            self._validate_file_uploads()

        except ValidationError as e:
            frappe.logger("customer_external_work_log").warning(
                f"Validation failed for External Work Log: {str(e)}"
            )
            frappe.throw(str(e))
        except Exception as e:
            frappe.logger("customer_external_work_log").error(
                f"Unexpected validation error for External Work Log: {str(e)}"
            )
            frappe.log_error(f"External Work Log Validation Error: {str(e)}", "Validation Error")
            raise

    def _validate_and_sanitize_inputs(self):
        """Comprehensive input validation and sanitization"""

        # Prepare data for validation
        validation_data = {}

        # Core fields validation
        if self.get("service_type"):
            validation_data["service_type"] = self.service_type
        if self.get("service_date"):
            validation_data["service_date"] = self.service_date
        if self.get("external_shop_name"):
            validation_data["external_shop_name"] = self.external_shop_name
        if self.get("service_notes"):
            validation_data["service_notes"] = self.service_notes
        if self.get("instrument"):
            validation_data["instrument"] = self.instrument

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
            "service_type": {
                "type": "select",
                "options": ["Inspection", "Setup", "Maintenance", "Repair", "Other"],
                "required": True,
            },
            "service_date": {
                "type": "date",
                "required": True,
                "max_date": "today",  # Cannot be in the future
            },
            "external_shop_name": {
                "type": "string",
                "required": False,
                "max_length": MAX_SHOP_NAME_LENGTH,
                "sanitize": True,
                "pattern": "alphanumeric_space",
            },
            "service_notes": {
                "type": "string",
                "required": False,
                "max_length": MAX_NOTES_LENGTH,
                "sanitize": True,
            },
            "instrument": {"type": "link", "target_doctype": "Instrument", "required": False},
        }

    def _validate_required_fields(self):
        """Validate required fields with enhanced checks"""

        if not self.get("service_type"):
            raise ValidationError(_("Service Type is required"))

        if not self.get("service_date"):
            raise ValidationError(_("Service Date is required"))

        # Require shop name for external services
        if not self.get("external_shop_name") or not self.external_shop_name.strip():
            raise ValidationError(_("External Shop Name is required"))

    def _validate_business_rules(self):
        """Validate business-specific rules and constraints"""

        # Service date validation
        if self.get("service_date"):
            if frappe.utils.getdate(self.service_date) > frappe.utils.getdate():
                raise ValidationError(_("Service date cannot be in the future"))

            # Check for reasonable historical limit (10 years)
            ten_years_ago = frappe.utils.add_years(frappe.utils.getdate(), -10)
            if frappe.utils.getdate(self.service_date) < ten_years_ago:
                raise ValidationError(_("Service date cannot be more than 10 years ago"))

        # Service type specific validation
        if self.get("service_type") == "Other" and not self.get("service_notes"):
            raise ValidationError(_('Service Notes are required when Service Type is "Other"'))

    def _validate_cross_references(self):
        """Validate cross-references and data consistency"""

        # Validate instrument link if provided
        if self.get("instrument") and not frappe.db.exists("Instrument", self.instrument):
            raise ValidationError(f"Invalid instrument reference: {self.instrument}")

        # Validate parent document exists and is accessible
        if self.get("parent") and self.get("parenttype"):
            if not frappe.db.exists(self.parenttype, self.parent):
                raise ValidationError(f"Invalid parent document reference: {self.parenttype} {self.parent}")

    def _validate_file_uploads(self):
        """Validate file uploads for security"""

        if self.get("receipt_attachment"):
            self._validate_receipt_file(self.receipt_attachment)

    def _validate_receipt_file(self, file_url: str):
        """Validate receipt file for security"""

        if not file_url:
            return

        try:
            # Get file document
            file_doc = frappe.get_doc("File", {"file_url": file_url})

            # Validate file extension
            file_extension = file_doc.get_extension().lower()
            if file_extension not in ALLOWED_FILE_EXTENSIONS:
                raise ValidationError(
                    f"Invalid file type for receipt. Allowed types: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
                )

            # Validate file size
            if file_doc.file_size and file_doc.file_size > (MAX_FILE_SIZE_MB * 1024 * 1024):
                raise ValidationError(f"Receipt file size exceeds {MAX_FILE_SIZE_MB}MB limit")

            # Additional validation for PDF receipts
            if file_extension == ".pdf":
                # Basic PDF validation - ensure it's actually a PDF
                if hasattr(file_doc, "content_type") and not file_doc.content_type.startswith(
                    "application/pdf"
                ):
                    raise ValidationError("Invalid PDF file format")

        except frappe.DoesNotExistError:
            raise ValidationError("Receipt file not found")

    def before_insert(self):
        """Pre-insertion processing with audit logging"""
        try:
            # Log creation for audit trail
            frappe.logger("customer_external_work_log").info(
                f"Creating external work log: service_type={self.get('service_type', 'Unknown')}, "
                f"shop={self.get('external_shop_name', 'Unknown')}, "
                f"user={frappe.session.user}"
            )

        except Exception as e:
            frappe.logger("customer_external_work_log").error(
                f"Failed to log external work log creation: {str(e)}"
            )

    def after_insert(self):
        """Post-insertion processing with notifications"""
        try:
            # Log successful creation
            frappe.logger("customer_external_work_log").info(
                f"Successfully created external work log: {self.name}"
            )

            # Notify relevant users if configured
            self._send_notifications()

        except Exception as e:
            frappe.logger("customer_external_work_log").error(f"Post-insert processing failed: {str(e)}")

    def _send_notifications(self):
        """Send notifications for new external work logs"""
        try:
            # Only send notifications for significant service types
            significant_services = ["Repair", "Setup", "Maintenance"]

            if self.get("service_type") in significant_services:
                # Get parent document to determine recipients
                if self.get("parent") and self.get("parenttype"):
                    # Determine recipients (Repair Managers first, then Technicians)
                    recipients = []
                    for role in ["Repair Manager", "Technician"]:
                        users_with_role = frappe.get_all("Has Role", filters={"role": role, "parenttype": "User"}, pluck="parent")
                        if users_with_role:
                            enabled_users = frappe.get_all("User", filters={"name": ["in", users_with_role], "enabled": 1}, pluck="name")
                            recipients.extend(enabled_users)
                        
                        if recipients:
                            break

                    if not recipients:
                        recipients = ["Administrator"]

                    # Deduplicate
                    recipients = list(set(recipients))

                    # Create notification for each recipient
                    for user in recipients:
                        notification_doc = frappe.get_doc(
                            {
                                "doctype": "Notification Log",
                                "subject": f"External {self.service_type} Logged",
                                "email_content": f"""
                            A new external {self.service_type.lower()} has been logged:

                            Shop: {self.get('external_shop_name', 'Unknown')}
                            Date: {self.get('service_date', 'Unknown')}
                            Notes: {self.get('service_notes', 'None')}
                            """,
                                "document_type": self.parenttype,
                                "document_name": self.parent,
                                "for_user": user,
                            }
                        )
                        notification_doc.insert(ignore_permissions=True)

        except Exception as e:
            frappe.logger("customer_external_work_log").warning(f"Failed to send notifications: {str(e)}")
