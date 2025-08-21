# File Header Template
# Relative Path: repair_portal/customer/doctype/consent_field_value/consent_field_value.py
# Last Updated: 2025-07-26
# Version: v1.0
# Purpose: Child table to store each consent form's field values
# Dependencies: Consent Form


from __future__ import annotations

from frappe.model.document import Document


class ConsentFieldValue(Document):
	"""
	Stores field label, type, and entered value for each filled consent.
	"""

	pass
