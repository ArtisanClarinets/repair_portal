# Path: repair_portal/customer/doctype/consent_template/consent_template.py
# Date: 2025-01-05
# Version: 3.0.0
# Description: Consent Template controller with Jinja validation, field management, and automation
# Dependencies: frappe, jinja2, frappe.utils

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, nowdate
from jinja2 import Environment, TemplateSyntaxError, select_autoescape


def _create_validation_environment() -> Environment:
    """Return a Jinja environment configured with HTML autoescaping."""
    return Environment(
        autoescape=select_autoescape(
            enabled_extensions=("html", "htm", "xml"),
            default=True,
            default_for_string=True,
        )
    )


class ConsentTemplate(Document):
    # Events ---------------------------------------------------------------

    @property
    def template_content(self) -> str | None:  # pragma: no cover - compatibility shim
        """Backward-compatible alias for renamed "content" field."""
        return getattr(self, "content", None)

    @template_content.setter
    def template_content(self, value: str | None) -> None:  # pragma: no cover - compatibility shim
        self.content = value  # type: ignore[assignment]

    def before_insert(self):
        """Initialize template before creation."""
        self._ensure_defaults()
        self._validate_template_syntax()

    def validate(self):
        """Comprehensive validation for template integrity."""
        # Basic field validation
        self._validate_required_fields()

        # Template content validation
        self._validate_template_syntax()

        # Required fields validation
        self._validate_required_fields_structure()

        # Usage validation (prevent deletion of active templates)
        self._validate_usage_constraints()

        # Auto-generate preview if content exists
        if self.content:
            self._generate_preview()

    def before_save(self):
        """Pre-save operations."""
        # Update modification tracking
        self.last_modified_on = now_datetime()  # type: ignore
        self.last_modified_by = frappe.session.user  # type: ignore

        # Set status based on disabled flag
        if getattr(self, "disabled", 0):
            self.status = "Inactive"  # type: ignore
        else:
            self.status = "Active"  # type: ignore

    def on_update(self):
        """Post-update operations."""
        # Update related consent forms if template structure changed
        self._update_related_forms()

    def before_cancel(self):
        """Prevent cancellation if template is in use."""
        if self._has_active_forms():
            frappe.throw(_("Cannot cancel template that has active consent forms"))

    # API Methods ----------------------------------------------------------

    @frappe.whitelist()
    def validate_template_syntax(self) -> dict[str, Any]:
        """Validate Jinja template syntax and return validation result."""
        return self._validate_template_syntax(return_result=True)

    @frappe.whitelist()
    def get_available_variables(self) -> list[str]:
        """Get list of available template variables."""
        variables = ["date", "form", "customer", "customer_name", "customer_email", "customer_phone"]

        # Add field variables from required fields
        for field in self.required_fields or []:
            if field.field_name:
                variables.append(frappe.scrub(field.field_name))

        # Add settings variables
        try:
            settings = frappe.get_single("Consent Settings")
            for mapping in settings.mappings or []:
                if getattr(mapping, "enabled", 0) and mapping.variable_name:
                    variables.append(mapping.variable_name)
        except Exception:
            pass

        return sorted(list(set(variables)))

    @frappe.whitelist()
    def preview_with_sample_data(self) -> str:
        """Generate preview with sample data for testing."""
        if not self.content:
            return _("No template content to preview")

        # Create sample context
        sample_context = self._build_sample_context()

        try:
            jenv = frappe.get_jenv()
            template = jenv.from_string(self.content)
            return template.render(sample_context)
        except Exception as e:
            return _("Preview generation failed: {0}").format(str(e))

    @frappe.whitelist()
    def duplicate_template(self, new_name: str) -> str:
        """Create a duplicate of this template with a new name."""
        if not frappe.has_permission(self.doctype, "create"):
            frappe.throw(_("Insufficient permissions to create template"))

        # Create new template
        new_template = frappe.copy_doc(self)
        new_template.template_name = new_name
        new_template.disabled = 1  # Start as disabled
        new_template.status = "Draft"  # type: ignore

        # Clear tracking fields
        new_template.last_modified_on = now_datetime()  # type: ignore
        new_template.last_modified_by = frappe.session.user  # type: ignore

        new_template.insert()

        return new_template.name

    @frappe.whitelist()
    def get_usage_statistics(self) -> dict[str, Any]:
        """Get statistics about template usage."""
        stats = {"total_forms": 0, "active_forms": 0, "submitted_forms": 0, "recent_forms": []}

        if frappe.db.exists("DocType", "Consent Form"):
            # Total forms using this template
            stats["total_forms"] = frappe.db.count("Consent Form", {"consent_template": self.name})

            # Active (draft) forms
            stats["active_forms"] = frappe.db.count(
                "Consent Form", {"consent_template": self.name, "docstatus": 0}
            )

            # Submitted forms
            stats["submitted_forms"] = frappe.db.count(
                "Consent Form", {"consent_template": self.name, "docstatus": 1}
            )

            # Recent forms (last 10)
            stats["recent_forms"] = frappe.db.get_all(
                "Consent Form",
                {"consent_template": self.name},
                ["name", "customer", "status", "creation"],
                order_by="creation desc",
                limit=10,
            )

        return stats

    # Helper Methods -------------------------------------------------------

    def _ensure_defaults(self) -> None:
        """Set default values for new templates."""
        if not getattr(self, "status", None):
            self.status = "Draft"  # type: ignore

        if not getattr(self, "last_modified_on", None):
            self.last_modified_on = now_datetime()  # type: ignore

        if not getattr(self, "last_modified_by", None):
            self.last_modified_by = frappe.session.user  # type: ignore

    def _validate_required_fields(self) -> None:
        """Validate required template fields."""
        if not self.template_name:
            frappe.throw(_("Template Name is required"))

        if not self.content:
            frappe.throw(_("Template Content is required"))

    def _validate_template_syntax(self, return_result: bool = False) -> dict[str, Any] | None:
        """Validate Jinja template syntax for the template content field."""
        source = self.content or ""
        if not source:
            if return_result:
                return {"valid": True, "message": "No content to validate"}
            return None

        try:
            _create_validation_environment().parse(source)
        except TemplateSyntaxError as exc:
            message = _("Invalid Jinja syntax in Consent Template content at line {0}: {1}").format(
                exc.lineno, exc.message
            )
            if return_result:
                return {"valid": False, "message": message}
            frappe.throw(message)
        except Exception as exc:  # pragma: no cover - defensive guard
            message = _("Template syntax validation failed: {0}").format(str(exc))
            if return_result:
                return {"valid": False, "message": message}
            frappe.throw(message)

        if return_result:
            return {"valid": True, "message": _("Template syntax is valid")}
        return None

    def _validate_required_fields_structure(self) -> None:
        """Validate required fields configuration."""
        if not self.required_fields:
            return

        # Check for duplicate field names (case-insensitive)
        field_names = []
        field_labels = []

        for field in self.required_fields:
            if not field.field_name:
                frappe.throw(_("Field Name is required for all required fields"))

            if not field.field_label:
                frappe.throw(_("Field Label is required for all required fields"))

            # Check for duplicates
            field_name_lower = field.field_name.lower()
            field_label_lower = field.field_label.lower()

            if field_name_lower in field_names:
                frappe.throw(_("Duplicate field name: {0}").format(field.field_name))

            if field_label_lower in field_labels:
                frappe.throw(_("Duplicate field label: {0}").format(field.field_label))

            field_names.append(field_name_lower)
            field_labels.append(field_label_lower)

            # Validate field types
            if field.field_type not in [
                "Data",
                "Text",
                "Select",
                "Check",
                "Date",
                "Datetime",
                "Int",
                "Float",
            ]:
                frappe.throw(_("Invalid field type: {0}").format(field.field_type))

    def _validate_usage_constraints(self) -> None:
        """Validate constraints based on template usage."""
        if self.is_new():
            return

        # Prevent disabling template with active forms
        if getattr(self, "disabled", 0) and self._has_active_forms():
            frappe.throw(_("Cannot disable template that has active consent forms"))

    def _has_active_forms(self) -> bool:
        """Check if template has active consent forms."""
        if not frappe.db.exists("DocType", "Consent Form"):
            return False

        return frappe.db.exists("Consent Form", {"consent_template": self.name, "docstatus": 0})

    def _generate_preview(self) -> None:
        """Generate preview content for display."""
        try:
            preview = self.preview_with_sample_data()
            self.preview_content = preview  # type: ignore
        except Exception:
            self.preview_content = _("Preview generation failed")  # type: ignore

    def _build_sample_context(self) -> dict[str, Any]:
        """Build sample context for testing template rendering."""
        context = {
            "date": nowdate(),
            "form": {"name": "FORM-001", "creation": now_datetime()},
            "customer": {"name": "CUST-001", "customer_name": "Sample Customer"},
            "customer_name": "Sample Customer",
            "customer_email": "sample@example.com",
            "customer_phone": "+1-555-0123",
        }

        # Add sample values for required fields
        for field in self.required_fields or []:
            if field.field_name:
                var_name = frappe.scrub(field.field_name)
                if field.field_type == "Check":
                    context[var_name] = True
                elif field.field_type in ["Int", "Float"]:
                    context[var_name] = 123
                elif field.field_type in ["Date", "Datetime"]:
                    context[var_name] = nowdate()
                else:
                    context[var_name] = field.default_value or f"Sample {field.field_label}"

        return context

    def _update_related_forms(self) -> None:
        """Update related consent forms when template changes."""
        if not frappe.db.exists("DocType", "Consent Form"):
            return

        # Find forms using this template
        forms = frappe.db.get_all(
            "Consent Form",
            {"consent_template": self.name, "docstatus": 0},  # Only update draft forms
            ["name"],
        )

        for form in forms:
            try:
                form_doc = frappe.get_doc("Consent Form", form.name)
                form_doc._ensure_required_fields()  # Sync new required fields
                form_doc.save(ignore_permissions=True)
            except Exception:
                # Don't fail the template save if form update fails
                frappe.log_error(f"Failed to update consent form: {form.name}")


# Public API ---------------------------------------------------------------


@frappe.whitelist()
def get_template_variables(template_name: str) -> list[str]:
    """Get available variables for a specific template."""
    try:
        template = frappe.get_doc("Consent Template", template_name)
        return template.get_available_variables()
    except frappe.DoesNotExistError:
        return []


@frappe.whitelist()
def validate_template_content(content: str) -> dict[str, Any]:
    """Validate template content without saving."""
    if not content:
        return {"valid": False, "message": "No content provided"}

    try:
        _create_validation_environment().parse(content)
        return {"valid": True, "message": "Template syntax is valid"}
    except TemplateSyntaxError as exc:
        message = _("Invalid Jinja syntax in Consent Template content at line {0}: {1}").format(
            exc.lineno, exc.message
        )
        return {"valid": False, "message": message}
    except Exception as exc:  # pragma: no cover - defensive guard
        return {"valid": False, "message": str(exc)}
