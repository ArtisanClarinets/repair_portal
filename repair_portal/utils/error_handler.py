# Enterprise Error Handling and Logging System
# Last Updated: 2025-07-19
# Version: v1.0
# Purpose: Fortune-500 level error handling for repair_portal

import json
import sys
import traceback
from enum import Enum
from typing import Any

import frappe
from frappe import _


class ErrorSeverity(Enum):
    """Error severity levels for proper categorization."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ErrorCategory(Enum):
    """Error categories for systematic handling."""

    VALIDATION = "Validation Error"
    PERMISSION = "Permission Error"
    DATABASE = "Database Error"
    INTEGRATION = "Integration Error"
    BUSINESS_LOGIC = "Business Logic Error"
    SYSTEM = "System Error"


class EnterpriseErrorHandler:
    """
    Comprehensive error handling system for repair_portal.
    Implements Fortune-500 standards for error tracking and resolution.
    """

    @staticmethod
    def handle_api_error(error: Exception, context: dict[str, Any] = None) -> dict[str, Any]:  # type: ignore
        """
        Centralized API error handling with proper logging and user feedback.

        Args:
            error: The exception that occurred
            context: Additional context information

        Returns:
            Standardized error response
        """
        context = context or {}

        # Determine error category and severity
        category = EnterpriseErrorHandler._categorize_error(error)
        severity = EnterpriseErrorHandler._determine_severity(error, category)

        # Generate error ID for tracking
        error_id = frappe.generate_hash(length=10)

        # Create comprehensive error log
        error_details = {
            "error_id": error_id,
            "category": category.value,
            "severity": severity.value,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "user": frappe.session.user,
            "timestamp": frappe.utils.now(),  # type: ignore
            "context": context,
            "request_data": EnterpriseErrorHandler._get_sanitized_request_data(),
            "system_info": EnterpriseErrorHandler._get_system_info(),
        }

        # Log to appropriate channels based on severity
        EnterpriseErrorHandler._log_error(error_details)

        # Send notifications for critical errors
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            EnterpriseErrorHandler._notify_administrators(error_details)

        # Return sanitized response to user
        return EnterpriseErrorHandler._create_user_response(error_details)

    @staticmethod
    def validate_business_rules(doc, validation_rules: list[dict]) -> list[str]:
        """
        Comprehensive business rule validation with detailed error reporting.

        Args:
            doc: Document to validate
            validation_rules: List of validation rule definitions

        Returns:
            List of validation error messages
        """
        errors = []

        for rule in validation_rules:
            try:
                rule_name = rule.get("name", "Unknown Rule")
                condition = rule.get("condition")
                message = rule.get("message", f"Validation failed for {rule_name}")
                severity = rule.get("severity", ErrorSeverity.MEDIUM)

                # Execute validation condition
                if condition and not EnterpriseErrorHandler._evaluate_condition(doc, condition):
                    errors.append(
                        {
                            "rule": rule_name,
                            "message": message,
                            "severity": severity.value,
                            "field": rule.get("field"),
                            "value": getattr(doc, rule.get("field", ""), None),
                        }
                    )

            except Exception as e:
                # Log validation rule execution error
                frappe.log_error(
                    f"Validation rule execution failed: {rule.get('name', 'Unknown')} - {str(e)}",
                    "Validation Rule Error",
                )

        return errors

    @staticmethod
    def create_error_dashboard_data() -> dict[str, Any]:
        """
        Generate error analytics for management dashboard.

        Returns:
            Error metrics and trends
        """
        try:
            # Get error statistics for last 30 days
            from_date = frappe.utils.add_days(frappe.utils.today(), -30)  # type: ignore

            error_stats = frappe.db.sql(
                """
                SELECT 
                    DATE(creation) as error_date,
                    error_category,
                    error_severity,
                    COUNT(*) as error_count
                FROM `tabError Log Enhanced`
                WHERE creation >= %s
                GROUP BY DATE(creation), error_category, error_severity
                ORDER BY error_date DESC
            """,
                (from_date,),
                as_dict=True,
            )

            # Calculate error trends
            total_errors = len(error_stats)  # type: ignore
            critical_errors = len([e for e in error_stats if e.get("error_severity") == "Critical"])  # type: ignore

            # Get top error categories
            category_counts = {}
            for stat in error_stats:
                category = stat.get("error_category", "Unknown")  # type: ignore
                category_counts[category] = category_counts.get(category, 0) + stat.get(  # type: ignore
                    "error_count", 0
                )  # type: ignore

            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            # Get resolution metrics
            resolved_errors = frappe.db.count(
                "Error Log Enhanced", {"creation": [">=", from_date], "status": "Resolved"}
            )

            resolution_rate = (resolved_errors / total_errors * 100) if total_errors > 0 else 0

            return {
                "total_errors": total_errors,
                "critical_errors": critical_errors,
                "resolution_rate": round(resolution_rate, 2),
                "top_categories": top_categories,
                "error_trends": error_stats,
                "last_updated": frappe.utils.now(),  # type: ignore
            }

        except Exception as e:
            frappe.log_error(f"Error dashboard data generation failed: {str(e)}")
            return {"error": "Failed to generate error dashboard data"}

    @staticmethod
    def _categorize_error(error: Exception) -> ErrorCategory:
        """Categorize error based on type and content."""
        error_type = type(error).__name__
        error_message = str(error).lower()

        if error_type in ["ValidationError", "MandatoryError"]:
            return ErrorCategory.VALIDATION
        elif error_type in ["PermissionError", "Forbidden"]:
            return ErrorCategory.PERMISSION
        elif "database" in error_message or "sql" in error_message:
            return ErrorCategory.DATABASE
        elif "api" in error_message or "integration" in error_message:
            return ErrorCategory.INTEGRATION
        elif error_type in ["ValueError", "TypeError"]:
            return ErrorCategory.BUSINESS_LOGIC
        else:
            return ErrorCategory.SYSTEM

    @staticmethod
    def _determine_severity(error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on type and category."""
        error_message = str(error).lower()

        # Critical errors
        if any(keyword in error_message for keyword in ["database", "connection", "timeout", "memory"]):
            return ErrorSeverity.CRITICAL

        # High severity errors
        if category in [ErrorCategory.DATABASE, ErrorCategory.SYSTEM] or (
            "permission" in error_message or "unauthorized" in error_message
        ):
            return ErrorSeverity.HIGH

        # Medium severity errors
        if category in [ErrorCategory.INTEGRATION, ErrorCategory.BUSINESS_LOGIC]:
            return ErrorSeverity.MEDIUM

        # Low severity errors (validation, etc.)
        return ErrorSeverity.LOW

    @staticmethod
    def _log_error(error_details: dict[str, Any]):
        """Log error to multiple channels based on configuration."""
        try:
            # Create enhanced error log document
            error_log = frappe.get_doc(
                {
                    "doctype": "Error Log Enhanced",
                    "error_id": error_details["error_id"],
                    "error_category": error_details["category"],
                    "error_severity": error_details["severity"],
                    "error_message": error_details["message"],
                    "traceback": error_details["traceback"],
                    "user": error_details["user"],
                    "context_data": json.dumps(error_details["context"]),
                    "request_data": json.dumps(error_details["request_data"]),
                    "system_info": json.dumps(error_details["system_info"]),
                    "status": "Open",
                    "resolution_notes": "",
                }
            )

            error_log.insert(ignore_permissions=True)

            # Also log to standard Frappe error log for compatibility
            frappe.log_error(
                title=f"[{error_details['severity']}] {error_details['category']}",
                message=f"Error ID: {error_details['error_id']}\n{error_details['message']}\n\n{error_details['traceback']}",
            )

        except Exception as e:
            # Fallback logging if enhanced logging fails
            print(f"Error logging failed: {str(e)}", file=sys.stderr)

    @staticmethod
    def _notify_administrators(error_details: dict[str, Any]):
        """Send notifications to administrators for critical errors."""
        try:
            # Get administrators
            admins = frappe.get_all(
                "User",
                filters={"role_profile_name": "System Manager", "enabled": 1},
                fields=["email"],
            )

            if not admins:
                return

            # Create notification
            subject = f"[CRITICAL] System Error - {error_details['error_id']}"
            message = f"""
            A critical error has occurred in the Repair Portal system.
            
            Error ID: {error_details['error_id']}
            Category: {error_details['category']}
            Severity: {error_details['severity']}
            User: {error_details['user']}
            Time: {error_details['timestamp']}
            
            Message: {error_details['message']}
            
            Please investigate immediately.
            """

            # Send email notifications
            for admin in admins:
                frappe.sendmail(recipients=[admin.email], subject=subject, message=message, delayed=False)

        except Exception as e:
            frappe.log_error(f"Administrator notification failed: {str(e)}")

    @staticmethod
    def _create_user_response(error_details: dict[str, Any]) -> dict[str, Any]:
        """Create sanitized error response for end users."""
        severity = error_details["severity"]

        # Different responses based on severity
        if severity == ErrorSeverity.CRITICAL.value:
            message = _(
                "A system error has occurred. Technical support has been notified. Please try again later."
            )
        elif severity == ErrorSeverity.HIGH.value:
            message = _(
                "An error occurred while processing your request. Please contact support if this persists."
            )
        else:
            # For medium/low severity, show the actual error message
            message = error_details["message"]

        return {
            "success": False,
            "error": True,
            "message": message,
            "error_id": error_details["error_id"],
            "severity": severity,
            "timestamp": error_details["timestamp"],
        }

    @staticmethod
    def _get_sanitized_request_data() -> dict[str, Any]:
        """Get sanitized request data for logging."""
        try:
            request_data = {}

            if hasattr(frappe.local, "form_dict"):
                # Remove sensitive fields from logging
                sensitive_fields = ["password", "api_key", "token", "secret"]

                for key, value in frappe.local.form_dict.items():
                    if not any(field in key.lower() for field in sensitive_fields):
                        request_data[key] = str(value)[:1000]  # Limit length

            return request_data

        except Exception:
            return {"error": "Failed to capture request data"}

    @staticmethod
    def _get_system_info() -> dict[str, Any]:
        """Get system information for error context."""
        try:
            return {
                "python_version": sys.version,
                "frappe_version": frappe.__version__,
                "site": frappe.local.site,
                "user_agent": frappe.get_request_header("User-Agent", ""),
                "ip_address": frappe.local.request_ip if hasattr(frappe.local, "request_ip") else None,
            }
        except Exception:
            return {"error": "Failed to capture system info"}

    @staticmethod
    def _evaluate_condition(doc, condition: str) -> bool:
        """
        Safely evaluate validation condition WITHOUT using eval().
        
        Supported condition patterns:
        - "doc.field_name" - truthy check
        - "doc.field_name and len(doc.field_name) >= N" - length check
        - "doc.field_name or doc.status == 'Draft'" - simple or with equality
        - "doc.field_name in ['A', 'B', 'C']" - membership check
        
        Returns True (pass) if the condition cannot be safely evaluated.
        """
        import operator
        import re
        
        try:
            condition = condition.strip()
            
            # Pattern: doc.field_name in ['val1', 'val2']
            in_match = re.match(r"doc\.(\w+)\s+in\s+\[(.+)\]", condition)
            if in_match:
                field_name = in_match.group(1)
                values_str = in_match.group(2)
                # Parse values safely - only allow string literals
                values = [v.strip().strip("'\"") for v in values_str.split(",")]
                field_value = getattr(doc, field_name, None)
                return field_value in values
            
            # Pattern: doc.field_name and len(doc.field_name) >= N
            len_match = re.match(r"doc\.(\w+)\s+and\s+len\(doc\.\1\)\s*(>=|>|<=|<|==)\s*(\d+)", condition)
            if len_match:
                field_name = len_match.group(1)
                op_str = len_match.group(2)
                threshold = int(len_match.group(3))
                field_value = getattr(doc, field_name, None)
                if not field_value:
                    return False
                ops = {">=": operator.ge, ">": operator.gt, "<=": operator.le, "<": operator.lt, "==": operator.eq}
                return ops.get(op_str, operator.ge)(len(field_value), threshold)
            
            # Pattern: doc.field_name or doc.field2 == 'Value'
            or_eq_match = re.match(r"doc\.(\w+)\s+or\s+doc\.(\w+)\s*==\s*['\"](.+)['\"]", condition)
            if or_eq_match:
                field1 = or_eq_match.group(1)
                field2 = or_eq_match.group(2)
                expected_value = or_eq_match.group(3)
                val1 = getattr(doc, field1, None)
                val2 = getattr(doc, field2, None)
                return bool(val1) or (val2 == expected_value)
            
            # Pattern: simple truthy check - doc.field_name
            simple_match = re.match(r"doc\.(\w+)$", condition)
            if simple_match:
                field_name = simple_match.group(1)
                return bool(getattr(doc, field_name, None))
            
            # If we can't safely parse the condition, log and return True (pass)
            frappe.log_error(
                f"Unsupported condition pattern: {condition}. "
                "Consider adding support for this pattern or simplifying the rule.",
                "Condition Evaluation Warning"
            )
            return True
            
        except Exception as e:
            frappe.log_error(f"Condition evaluation failed: {condition} - {str(e)}")
            return True  # Default to pass if evaluation fails


# Example usage patterns:


def safe_api_call(func):
    """Decorator for safe API calls with comprehensive error handling."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return EnterpriseErrorHandler.handle_api_error(
                e, {"function": func.__name__, "args": str(args)[:500], "kwargs": str(kwargs)[:500]}
            )

    return wrapper


# Example business validation rules:
INSTRUMENT_VALIDATION_RULES = [
    {
        "name": "Serial Number Required",
        "condition": "doc.serial_no and len(doc.serial_no) >= 6",
        "message": "Serial number must be at least 6 characters",
        "severity": ErrorSeverity.HIGH,
        "field": "serial_no",
    },
    {
        "name": "Customer Assignment",
        "condition": "doc.customer or doc.status == 'Draft'",
        "message": "Customer must be assigned for non-draft instruments",
        "severity": ErrorSeverity.MEDIUM,
        "field": "customer",
    },
    {
        "name": "Valid Workflow State",
        "condition": "doc.workflow_state in ['Draft', 'Active', 'Archived', 'Maintenance']",
        "message": "Invalid workflow state specified",
        "severity": ErrorSeverity.HIGH,
        "field": "workflow_state",
    },
]
