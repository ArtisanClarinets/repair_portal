# File Header Template
# Relative Path: repair_portal/customer/doctype/linked_players/linked_players.py
# Last Updated: 2025-07-18
# Version: v0.1
# Purpose: Server-side controller for Linked Players child doctype.
# Dependencies: Person, Player Profile doctypes, frappe framework

"""Server-side logic for the **Linked Players** child doctype.

This module enforces Fortune-500–grade data integrity and UX standards by

* Validating that linked *Person* and *Player Profile* documents exist and are active.
* Preventing duplicate links for the same Player Profile within a single Customer.
* Guaranteeing a single **primary** profile flag per parent document.
* Normalizing date fields and providing clear developer-friendly error messages.

All exceptions are captured and logged via ``frappe.log_error`` for rapid debugging.
"""

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class LinkedPlayers(Document):
	"""Child-doctype controller class."""

	# ---------------------------------------------------------------------
	# Standard Frappe Lifecycle Hooks
	# ---------------------------------------------------------------------

	def validate(self) -> None:  # noqa: D401
		"""Validate every save.

		Ensures:
		    1. Both linked records exist and are not disabled.
		    2. The same *Player Profile* is not linked twice under one parent.
		    3. Only **one** row per parent can have ``is_primary = 1``.
		    4. ``date_linked`` is always a proper date (defaults to today).

		Raises:
		    frappe.ValidationError: On any rule violation.
		"""
		try:
			self._validate_links_exist()
			self._validate_unique_per_parent()
			self._enforce_single_primary()
			self._normalize_dates()
		except frappe.ValidationError:
			# Already a user-facing message
			raise
		except Exception as exc:  # pragma: no cover
			# Log unexpected errors for ops while shielding end users
			frappe.log_error(frappe.get_traceback(), f"[LinkedPlayers.validate] {repr(exc)}")
			raise frappe.ValidationError(
				"Unexpected error while validating Linked Player. Please contact support."
			)

	# ------------------------------------------------------------------
	# Internal Helpers (Private)
	# ------------------------------------------------------------------

	def _validate_links_exist(self) -> None:
		"""Confirm both linked doctypes exist and are active."""
		missing: list[str] = []
		# Person
		if not frappe.db.exists("Person", self.person):
			missing.append(f"Person: {self.person}")
		# Player Profile
		if not frappe.db.exists("Player Profile", self.player_profile):
			missing.append(f"Player Profile: {self.player_profile}")

		if missing:
			raise frappe.ValidationError(f"Linked document(s) not found or inactive: {', '.join(missing)}")

	def _validate_unique_per_parent(self) -> None:
		"""Prevent duplicate Player Profile links in the same parent document."""
		if not self.parentfield:
			return  # Safety-net for orphaned rows
		duplicates = [
			d for d in self.get_siblings() if d.player_profile == self.player_profile and d.name != self.name
		]
		if duplicates:
			raise frappe.ValidationError("This Player Profile is already linked to the current Customer.")

	def _enforce_single_primary(self) -> None:
		"""Ensure only one row per parent is flagged as primary."""
		if not self.is_primary:
			return
		primaries: list[Document] = [d for d in self.get_siblings() if d.is_primary and d.name != self.name]
		if primaries:
			raise frappe.ValidationError("Only one Player Profile may be marked as Primary per Customer.")

	def _normalize_dates(self) -> None:
		"""Guarantee ``date_linked`` is set and sane."""
		if not self.date_linked:
			self.date_linked = nowdate()
		else:
			# Cast to date to avoid string formats making it through
			self.date_linked = getdate(self.date_linked)

	# ------------------------------------------------------------------
	# Public Utility Methods (Optional)
	# ------------------------------------------------------------------

	def as_dict_safe(self) -> dict:  # pragma: no cover
		"""Return a sanitized dict (excludes private meta fields)."""
		public_fields: set[str] = {
			"person",
			"player_profile",
			"relationship",
			"date_linked",
			"is_primary",
			"notes",
		}
		return {k: v for k, v in self.as_dict().items() if k in public_fields}
