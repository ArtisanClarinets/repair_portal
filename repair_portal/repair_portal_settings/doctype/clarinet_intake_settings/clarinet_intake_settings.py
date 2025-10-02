# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/repair_portal_settings/doctype/clarinet_intake_settings/clarinet_intake_settings.py
# Last Updated: 2025-09-19
# Version: v1.2
# Purpose:
#   Backend controller for Clarinet Intake Settings (Single doctype).
#   • Validates link-type defaults (Item Group, Warehouse, Price Lists, UOM)
#   • Provides get_intake_settings() utility with sane fallbacks
# Dependencies: frappe (v15)

from __future__ import annotations

import frappe
from frappe.model.document import Document


class ClarinetIntakeSettings(Document):
	"""Settings DocType controller for Intake automation."""

	def validate(self):
		"""Ensure referenced records exist; apply safe fallbacks where appropriate."""
		self._validate_link("default_item_group", "Item Group", fallback="Clarinets")
		self._validate_link("default_inspection_warehouse", "Warehouse")
		self._validate_link("buying_price_list", "Price List", fallback="Standard Buying")
		self._validate_link("selling_price_list", "Price List", fallback="Standard Selling")
		self._validate_link("stock_uom", "UOM", fallback="Nos")
		self._validate_consent_template()

		# Ensure at least one naming hint is present
		if not (self.intake_naming_series or self.intake_id_pattern):
			# Provide a conservative default pattern compatible with make_autoname
			self.intake_id_pattern = "CI-.{YYYY}.-.#####"

	def _validate_link(self, fieldname: str, doctype: str, fallback: str | None = None) -> None:
		val = (getattr(self, fieldname, None) or "").strip()
		if not val:
			if fallback and frappe.db.exists(doctype, fallback):
				setattr(self, fieldname, fallback)
			return

		if not frappe.db.exists(doctype, val):
			if fallback and frappe.db.exists(doctype, fallback):
				setattr(self, fieldname, fallback)
			else:
				frappe.msgprint(
					f"Referenced {doctype} <b>{frappe.as_unicode(val)}</b> not found; clearing the field.",
					indicator="orange",
				)
				setattr(self, fieldname, None)

	def _validate_consent_template(self) -> None:
		"""Validate consent template if auto-create is enabled."""
		if self.auto_create_consent_form and self.default_consent_template:  # type: ignore
			if not frappe.db.exists("Consent Template", self.default_consent_template):  # type: ignore
				frappe.msgprint(
					_("Consent Template '{0}' not found. Please select a valid template.").format(
						self.default_consent_template  # type: ignore
					),
					indicator="orange"
				)
				self.default_consent_template = None  # type: ignore


def get_intake_settings() -> dict:
	"""
	Return Clarinet Intake Settings as a dict with sensible fallbacks.
	Keys used elsewhere include:
	  - default_item_group (Link → Item Group)
	  - stock_uom (Link → UOM)
	  - auto_create_initial_setup (Check)
	  - require_inspection (Check)
	  - notify_on_stock_issue (Check)
	  - auto_normalize_brand (Check)
	  - intake_naming_series (Data)
	  - intake_id_pattern (Data)
	"""
	doc = frappe.get_single("Clarinet Intake Settings")
	data = doc.as_dict()

	# Fallbacks to keep upstream controllers resilient
	if not data.get("default_item_group"):
		data["default_item_group"] = "Clarinets" if frappe.db.exists("Item Group", "Clarinets") else None
	if not data.get("stock_uom"):
		data["stock_uom"] = "Nos" if frappe.db.exists("UOM", "Nos") else None

	# Naming hint: prefer intake_naming_series if present, else pattern
	if not data.get("intake_naming_series") and not data.get("intake_id_pattern"):
		data["intake_id_pattern"] = "CI-.{YYYY}.-.#####"  # safe default

	return data
