# Path: repair_portal/repair_portal/customer/doctype/consent_required_field/consent_required_field.py
# Date: 2025-01-27
# Version: 2.0.0
# Description: Child table for required fields in Consent Template with validation and auto-completion
# Dependencies: frappe.model.document, consent template system


import frappe
from frappe import _
from frappe.model.document import Document


class ConsentRequiredField(Document):
    """
    Child table for listing dynamic required fields in Consent Templates.

    Defines field structure, validation rules, and UI behavior for consent forms.
    Supports auto-completion and field type validation.
    """

    def validate(self) -> None:
        """Validate required field configuration"""
        self._validate_required_fields()
        self._validate_field_type()
        self._validate_options()
        self._set_defaults()

    def _validate_required_fields(self) -> None:
        """Validate required fields"""
        if not self.field_label:
            frappe.throw(_("Field Label is required"))

        if not self.field_type:
            frappe.throw(_("Field Type is required"))

    def _validate_field_type(self) -> None:
        """Validate field type against allowed values"""
        allowed_types = [
            "Data",
            "Int",
            "Date",
            "Float",
            "Small Text",
            "Text",
            "Check",
            "Signature",
            "Select",
            "Link",
        ]

        if self.field_type not in allowed_types:
            frappe.throw(_("Invalid field type: {0}").format(self.field_type))

    def _validate_options(self) -> None:
        """Validate options for Select and Link fields"""
        if self.field_type == "Select" and not self.options:
            frappe.throw(_("Options are required for Select field"))

        if self.field_type == "Link" and not self.options:
            frappe.throw(_("Link DocType is required for Link field"))

        # Validate Link DocType exists
        if self.field_type == "Link" and self.options:
            if not frappe.db.exists("DocType", self.options):
                frappe.throw(_("DocType {0} does not exist").format(self.options))

    def _set_defaults(self) -> None:
        """Set default values"""
        if not self.idx:
            # Get next index
            parent_doc = self.parent_doc if hasattr(self, "parent_doc") else None
            if parent_doc and hasattr(parent_doc, "required_fields"):
                self.idx = len(parent_doc.required_fields) + 1

    @frappe.whitelist()
    def get_field_definition(self) -> dict[str, any]:
        """Get field definition for form rendering"""
        field_def = {
            "fieldname": frappe.scrub(self.field_label),
            "fieldtype": self.field_type,
            "label": self.field_label,
            "reqd": 1 if self.is_required else 0,
        }

        if self.default_value:
            field_def["default"] = self.default_value

        if hasattr(self, "options") and self.options:
            field_def["options"] = self.options

        return field_def

    def get_validation_rules(self) -> dict[str, any]:
        """Get validation rules for client-side validation"""
        rules = {}

        if self.is_required:
            rules["required"] = True

        if self.field_type == "Int":
            rules["type"] = "number"
            rules["step"] = "1"
        elif self.field_type == "Float":
            rules["type"] = "number"
            rules["step"] = "any"
        elif self.field_type == "Date":
            rules["type"] = "date"

        return rules

    def generate_fieldname(self) -> str:
        """Generate fieldname from label if not provided"""
        if self.field_label:
            return frappe.scrub(self.field_label)
        return "field_" + str(self.idx or 1)
