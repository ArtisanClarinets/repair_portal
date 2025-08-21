# File Header Template
# Relative Path: repair_portal/intake/doctype/clarinet_intake_settings/clarinet_intake_settings.py
# Last Updated: 2025-07-21
# Version: v1.1
# Purpose: Backend controller for Clarinet Intake Settings. Handles field validation for table fields and provides a utility for all business logic to fetch settings.
# Dependencies: frappe (v15)

import frappe
from frappe.model.document import Document


class ClarinetIntakeSettings(Document):
	"""Settings DocType controller for Intake automation."""

	# No JSON validation needed—table is self-validating.
	pass


# Utility to fetch all settings as a dict for business logic


def get_intake_settings():
	"""Returns Clarinet Intake Settings as a dict."""
	return frappe.get_single("Clarinet Intake Settings").as_dict()
