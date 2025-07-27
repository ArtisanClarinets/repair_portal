# File Header Template
# Relative Path: repair_portal/customer/doctype/consent_form/consent_form.py
# Last Updated: 2025-07-26
# Version: v1.0
# Purpose: Backend controller for Consent Form - generates, validates, and renders filled agreements
# Dependencies: Consent Template, Consent Required Field, Consent Field Value

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class ConsentForm(Document):
    """
    Backend controller for Consent Form DocType.
    Handles dynamic field value filling and renders the completed agreement using the Consent Template.
    """

    def validate(self):
        # Validate required fields are filled
        template = frappe.get_doc("Consent Template", self.consent_template)
        required_fields = {f.field_label for f in template.required_fields}
        provided_fields = {f.field_label for f in self.consent_field_values}
        missing = required_fields - provided_fields
        if missing:
            frappe.throw(f"Missing required field(s): {', '.join(missing)}")

    def before_save(self):
        if self.status == "Signed":
            # Render the final agreement
            self.rendered_content = self.render_agreement()
            self.signed_on = now_datetime()

    def render_agreement(self) -> str:
        """
        Merges all field values into the Consent Template and returns HTML content.
        Returns:
            str: The rendered agreement with placeholders replaced by field values.
        """
        template = frappe.get_doc("Consent Template", self.consent_template)
        content = template.content
        # Replace placeholders like [Field Label] with actual values
        for field in self.consent_field_values:
            content = content.replace(f"[{field.field_label}]", field.field_value or "___________")
        # Insert signature as base64 image or placeholder text
        content = content.replace("[Signature]", "<b>Signed:</b> ____________" if not self.signature else "<b>Signed:</b> <img src='{}' style='height:40px;'>".format(self.signature))
        return content
