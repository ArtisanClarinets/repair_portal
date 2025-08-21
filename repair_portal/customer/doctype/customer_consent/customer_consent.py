# File Header Template
# Relative Path: repair_portal/customer/doctype/customer_consent/customer_consent.py
# Last Updated: 2025-07-26
# Version: v1.0
# Purpose: Holds completed customer consent forms, filled values, signature, and locked HTML.
# Dependencies: Consent Template, Consent Field Value

import frappe
from frappe.model.document import Document


class CustomerConsent(Document):
	"""
	Represents a filled customer consent form, with dynamic fields, signature, and locked output.
	Args:
	    Document (frappe.model.document.Document): Frappe base document class
	Returns:
	    None
	"""

	def autoname(self):
		"""Use a hash of customer/template/timestamp for unique name."""
		import hashlib
		import time

		key = f"{self.customer}-{self.consent_template}-{self.signed_on or time.time()}"
		self.name = hashlib.sha1(key.encode()).hexdigest()[:20]

	def validate(self):
		"""
		On save/submit: Generate the rendered HTML consent, replacing placeholders with field values.
		Attach signature image if present.
		"""
		try:
			template = frappe.get_doc("Consent Template", self.consent_template)
			content = template.content
			field_map = {v.field_label: v.field_value for v in self.field_values}
			for key, val in field_map.items():
				content = content.replace(f"[{key}]", frappe.safe_decode(val or ""))
			if self.signature:
				content += f'<br><b>Signature:</b><br><img src="{self.signature}" height="90">'
			content += f"<br><b>Signed On:</b> {self.signed_on}"
			self.rendered_content = content
		except Exception as e:
			frappe.log_error(f"Consent form rendering error: {e}", "CustomerConsent")
