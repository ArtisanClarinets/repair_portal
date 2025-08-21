# File Header Template
# Relative Path: repair_portal/customer/doctype/consent_form/consent_form.py
# Last Updated: 2025-07-28
# Version: v1.1
# Purpose: Backend controller for Consent Form - generates, validates, and renders filled agreements
# Dependencies: Consent Template, Consent Required Field, Consent Field Value

from __future__ import annotations

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
		Auto-fills company info and date fields.
		Returns:
		    str: The rendered agreement with placeholders replaced by field values.
		"""
		template = frappe.get_doc("Consent Template", self.consent_template)
		content = template.content

		# --- 1. Auto-fill: Company Info ---
		try:
			# Try to use Frappe standard Company Doc
			company = frappe.get_doc(
				"Company", frappe.db.get_single_value("Global Defaults", "default_company")
			)
			company_info = {
				"[Your Company Name]": company.company_name,
				"[Your Company Address]": getattr(company, "address", "") or "",
				"[Your Company Phone Number]": getattr(company, "phone", "") or "",
				"[Your Company Email / Website]": getattr(company, "email", "") or "",
			}
		except Exception:
			# Fallback: safe defaults
			company_info = {
				"[Your Company Name]": "",
				"[Your Company Address]": "",
				"[Your Company Phone Number]": "",
				"[Your Company Email / Website]": "",
			}

		for placeholder, value in company_info.items():
			content = content.replace(placeholder, value or "___________")

		# --- 2. Auto-fill: Date ---
		from datetime import datetime

		_date = self.signed_on if self.signed_on else now_datetime()
		if isinstance(_date, str):
			try:
				_date = datetime.fromisoformat(_date)
			except Exception:
				_date = now_datetime()
		content = content.replace("[Date]", _date.strftime("%Y-%m-%d"))

		# --- 3. Fill dynamic fields ---
		for field in self.consent_field_values:
			content = content.replace(f"[{field.field_label}]", field.field_value or "___________")

		# --- 4. Signature ---
		content = content.replace(
			"[Signature]",
			"<b>Signed:</b> ____________"
			if not self.signature
			else f"<b>Signed:</b> <img src='{self.signature}' style='height:40px;'>",
		)
		return content
