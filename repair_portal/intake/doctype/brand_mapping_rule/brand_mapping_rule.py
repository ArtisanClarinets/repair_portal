# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/doctype/brand_mapping_rule/brand_mapping_rule.py
# Last Updated: 2025-09-19
# Version: v1.2.0 (Normalization + case-insensitive uniqueness + reusable map_brand helper)
# Purpose:
#   Define brand mapping rules for instrument profiles in the Repair Portal, ensuring consistent brand naming.
#   • Normalizes inputs (trim, collapse whitespace) and performs case-insensitive duplicate checks
#   • Exposes map_brand(name: str) -> str for controller reuse
# Dependencies: Frappe Framework (Document API)

from __future__ import annotations

import re

import frappe
from frappe import _
from frappe.model.document import Document

# Simple in-process cache to avoid repeated full scans during a single request
_brand_map_cache_key = "repair_portal__brand_map_cache"


def _collapse_ws(s: str) -> str:
	"""Trim and collapse internal whitespace to single spaces."""
	return re.sub(r"\s+", " ", (s or "").strip())


def _normalized_for_compare(s: str) -> str:
	"""Normalization used for comparisons (trim/collapse + casefold)."""
	return _collapse_ws(s).casefold()


class BrandMappingRule(Document):
	"""
	Controller for managing brand mapping rules.
	This document defines how external brand names (from_brand) map to standardized brand names (to_brand).
	"""

	def validate(self):
		"""Normalize input and enforce case-insensitive uniqueness of from_brand."""
		# Normalize fields for storage (trim + collapse internal whitespace)
		self.from_brand = _collapse_ws(self.from_brand)  # type: ignore
		self.to_brand = _collapse_ws(self.to_brand)      # type: ignore

		# Required checks
		if not self.from_brand:  # type: ignore
			frappe.throw(_("From Brand is required"))
		if not self.to_brand:  # type: ignore
			frappe.throw(_("Mapped Brand is required"))

		# Enforce case-insensitive uniqueness on from_brand (across all rows)
		self._validate_unique_from_brand()

		# Invalidate the cache so subsequent lookups reflect this change
		if hasattr(frappe.local, _brand_map_cache_key):
			delattr(frappe.local, _brand_map_cache_key)

	def _validate_unique_from_brand(self) -> None:
		"""Ensure there is no other row whose normalized from_brand equals ours."""
		target_norm = _normalized_for_compare(self.from_brand)  # type: ignore

		# Pull all sibling rules (child table rows live globally)
		rows = frappe.get_all(
			"Brand Mapping Rule",
			fields=["name", "from_brand"],
		)

		for r in rows:
			if r.get("name") == self.name:
				continue
			other_norm = _normalized_for_compare(r.get("from_brand") or "")
			if other_norm == target_norm:
				frappe.throw(
					_("A mapping for source brand '{0}' already exists (case-insensitive match).").format(
						self.from_brand  # type: ignore
					)
				)


def _load_brand_map() -> dict[str, str]:
	"""
	Load all brand mappings into a dict keyed by normalized from_brand (case-insensitive),
	values are the stored to_brand strings.
	"""
	cache = getattr(frappe.local, _brand_map_cache_key, None)
	if cache is not None:
		return cache

	rows = frappe.get_all("Brand Mapping Rule", fields=["from_brand", "to_brand"])
	brand_map: dict[str, str] = {}
	for r in rows:
		f = _normalized_for_compare(r.get("from_brand") or "")
		t = _collapse_ws(r.get("to_brand") or "")
		if f:
			# Last-one-wins if duplicates somehow exist; validation should prevent it
			brand_map[f] = t

	setattr(frappe.local, _brand_map_cache_key, brand_map)
	return brand_map


def map_brand(name: str | None) -> str | None:
	"""
	Return the mapped/standardized brand for a given input, if a rule exists.
	Normalization: trim + collapse whitespace; case-insensitive match on source brand.
	"""
	if not name:
		return name
	m = _load_brand_map()
	return m.get(_normalized_for_compare(name), _collapse_ws(name))
