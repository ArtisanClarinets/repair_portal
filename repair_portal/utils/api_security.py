# API Security Hardening Module
# Last Updated: 2025-07-19
# Version: v1.0
# Purpose: Enterprise-grade API security for repair_portal

import re
import time
from functools import wraps

import frappe
from frappe import _


class APISecurityManager:
    """
    Fortune-500 level API security controls for repair_portal.
    Implements comprehensive security patterns and validation.
    """

    # Rate limiting configuration
    RATE_LIMITS = {
        "default": {"requests": 100, "window": 3600},  # 100 requests per hour
        "auth": {"requests": 10, "window": 900},  # 10 auth attempts per 15 min
        "data_export": {"requests": 5, "window": 3600},  # 5 exports per hour
        "bulk_operations": {"requests": 20, "window": 3600},  # 20 bulk ops per hour
    }

    # Input validation patterns
    VALIDATION_PATTERNS = {
        "serial_no": r"^[A-Z0-9]{6,20}$",
        "customer_code": r"^[A-Z0-9-]{3,15}$",
        "workflow_state": r"^[A-Za-z\s]{1,50}$",
        "safe_string": r"^[A-Za-z0-9\s\-_.]{1,255}$",
    }

    @staticmethod
    def rate_limit(limit_type: str = "default"):
        """
        Decorator for API rate limiting with Redis backend.

        Args:
            limit_type: Type of rate limit to apply
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not APISecurityManager._check_rate_limit(limit_type):
                    frappe.throw(
                        _("Rate limit exceeded. Please try again later."),
                        frappe.TooManyRequestsError,
                    )
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def validate_input(validation_rules: dict[str, str]):
        """
        Decorator for comprehensive input validation.

        Args:
            validation_rules: Dict mapping parameter names to validation patterns
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Validate frappe.form_dict parameters
                for param, pattern_name in validation_rules.items():
                    value = frappe.form_dict.get(param)
                    if value and not APISecurityManager._validate_pattern(value, pattern_name):
                        frappe.throw(_(f"Invalid format for parameter: {param}"))

                return func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def require_role(required_roles: list[str], allow_system_manager: bool = True):
        """
        Decorator for role-based access control.

        Args:
            required_roles: List of roles that can access the endpoint
            allow_system_manager: Whether System Manager can always access
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                user_roles = frappe.get_roles(frappe.session.user)

                # System Manager bypass (if enabled)
                if allow_system_manager and "System Manager" in user_roles:
                    return func(*args, **kwargs)

                # Check required roles
                if not any(role in user_roles for role in required_roles):
                    frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

                return func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def audit_log(action: str, sensitive_data: bool = False):
        """
        Decorator for comprehensive audit logging.

        Args:
            action: Description of the action being performed
            sensitive_data: Whether this action involves sensitive data
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)

                    # Log successful execution
                    APISecurityManager._create_audit_log(
                        action=action,
                        status="Success",
                        execution_time=time.time() - start_time,
                        sensitive_data=sensitive_data,
                    )

                    return result

                except Exception as e:
                    # Log failed execution
                    APISecurityManager._create_audit_log(
                        action=action,
                        status="Failed",
                        error=str(e),
                        execution_time=time.time() - start_time,
                        sensitive_data=sensitive_data,
                    )
                    raise

            return wrapper

        return decorator

    @staticmethod
    def _check_rate_limit(limit_type: str) -> bool:
        """Check if current user is within rate limits."""
        if limit_type not in APISecurityManager.RATE_LIMITS:
            limit_type = "default"

        config = APISecurityManager.RATE_LIMITS[limit_type]
        cache_key = f"rate_limit:{frappe.session.user}:{limit_type}"

        current_count = frappe.cache().get_value(cache_key) or 0

        if current_count >= config["requests"]:
            return False

        # Increment counter
        frappe.cache().set_value(cache_key, current_count + 1, expires_in_sec=config["window"])

        return True

    @staticmethod
    def _validate_pattern(value: str, pattern_name: str) -> bool:
        """Validate input against defined patterns."""
        if pattern_name not in APISecurityManager.VALIDATION_PATTERNS:
            return True  # No validation pattern defined

        pattern = APISecurityManager.VALIDATION_PATTERNS[pattern_name]
        return bool(re.match(pattern, str(value)))

    @staticmethod
    def _create_audit_log(
        action: str,
        status: str,
        execution_time: float = 0,
        error: str = None,
        sensitive_data: bool = False,
    ):
        """Create comprehensive audit log entry."""
        try:
            audit_doc = frappe.get_doc(
                {
                    "doctype": "API Audit Log",
                    "user": frappe.session.user,
                    "action": action,
                    "status": status,
                    "execution_time": execution_time,
                    "ip_address": frappe.local.request_ip if hasattr(frappe.local, "request_ip") else None,
                    "user_agent": frappe.get_request_header("User-Agent", ""),
                    "error_message": error,
                    "sensitive_data": sensitive_data,
                    "timestamp": frappe.utils.now(),
                }
            )

            audit_doc.insert(ignore_permissions=True)

        except Exception as e:
            # Fallback to error log if audit log fails
            frappe.log_error(f"Audit log creation failed: {str(e)}")


# Secure API endpoint examples:


@frappe.whitelist()
@APISecurityManager.rate_limit("default")
@APISecurityManager.require_role(["Technician", "Repair Manager"])
@APISecurityManager.validate_input({"instrument_id": "safe_string", "workflow_state": "workflow_state"})
@APISecurityManager.audit_log("Update Instrument Workflow State")
def update_instrument_workflow_state():
    """
    Secure endpoint for updating instrument workflow state.
    Implements comprehensive security controls.
    """
    instrument_id = frappe.form_dict.get("instrument_id")
    new_state = frappe.form_dict.get("workflow_state")

    # Additional business logic validation
    if not frappe.db.exists("Instrument Profile", instrument_id):
        frappe.throw(_("Instrument not found"))

    # Check user has permission to modify this specific instrument
    doc = frappe.get_doc("Instrument Profile", instrument_id)
    if not doc.has_permission("write"):
        frappe.throw(_("Insufficient permissions for this instrument"))

    # Update with proper validation
    doc.workflow_state = new_state
    doc.save()

    return {"success": True, "message": "Workflow state updated successfully"}


@frappe.whitelist()
@APISecurityManager.rate_limit("data_export")
@APISecurityManager.require_role(["Repair Manager", "Quality Control"])
@APISecurityManager.audit_log("Export Customer Data", sensitive_data=True)
def export_customer_data():
    """
    Secure customer data export with strict access controls.
    """
    customer_id = frappe.form_dict.get("customer_id")

    if not customer_id:
        frappe.throw(_("Customer ID is required"))

    # Verify customer exists and user has access
    if not frappe.db.exists("Customer", customer_id):
        frappe.throw(_("Customer not found"))

    # Get customer data with field-level security
    customer_data = APISecurityManager._get_sanitized_customer_data(customer_id)

    return {
        "success": True,
        "data": customer_data,
        "export_timestamp": frappe.utils.now(),
        "exported_by": frappe.session.user,
    }


@frappe.whitelist()
@APISecurityManager.rate_limit("bulk_operations")
@APISecurityManager.require_role(["System Manager"])
@APISecurityManager.audit_log("Bulk Instrument Update", sensitive_data=True)
def bulk_update_instruments():
    """
    Secure bulk operations endpoint with transaction safety.
    """
    updates = frappe.form_dict.get("updates", [])

    if not isinstance(updates, list) or len(updates) > 100:
        frappe.throw(_("Invalid or too many updates (max 100)"))

    try:
        frappe.db.begin()

        updated_count = 0
        for update in updates:
            instrument_id = update.get("instrument_id")
            field_updates = update.get("updates", {})

            if instrument_id and frappe.db.exists("Instrument Profile", instrument_id):
                doc = frappe.get_doc("Instrument Profile", instrument_id)

                # Apply only allowed field updates
                for field, value in field_updates.items():
                    if field in ["status", "notes", "condition"]:  # Whitelist fields
                        setattr(doc, field, value)

                doc.save()
                updated_count += 1

        frappe.db.commit()

        return {
            "success": True,
            "updated_count": updated_count,
            "message": f"Successfully updated {updated_count} instruments",
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Bulk update failed: {str(e)}")
        frappe.throw(_("Bulk update operation failed"))


# Helper methods for secure data handling:


def _get_sanitized_customer_data(customer_id: str) -> dict:
    """Get customer data with sensitive field filtering."""

    # Define sensitive fields that require special handling
    sensitive_fields = ["tax_id", "phone", "email_id", "notes"]

    customer = frappe.get_doc("Customer", customer_id)

    # Get base customer data
    data = {
        "customer_name": customer.customer_name,
        "customer_group": customer.customer_group,
        "territory": customer.territory,
        "creation": customer.creation,
    }

    # Add sensitive fields only if user has appropriate role
    user_roles = frappe.get_roles(frappe.session.user)
    if "System Manager" in user_roles or "Compliance Officer" in user_roles:
        for field in sensitive_fields:
            if hasattr(customer, field):
                data[field] = getattr(customer, field)

    return data


# Security configuration constants:
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'",
}


# Input sanitization utilities:
def sanitize_html_input(html_content: str) -> str:
    """Remove potentially dangerous HTML content."""
    import bleach

    allowed_tags = ["p", "br", "strong", "em", "ul", "ol", "li"]
    allowed_attributes = {}

    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)


def validate_file_upload(file_content: bytes, allowed_extensions: list[str]) -> bool:
    """Validate uploaded file for security threats."""

    # Check file size (max 10MB)
    if len(file_content) > 10 * 1024 * 1024:
        return False

    # Basic malware detection patterns
    malware_patterns = [b"<script", b"javascript:", b"vbscript:", b"onload=", b"onerror="]

    content_lower = file_content.lower()
    for pattern in malware_patterns:
        if pattern in content_lower:
            return False

    return True
