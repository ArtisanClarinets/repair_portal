# repair_portal/repair_portal/scripts/doctype_loader.py
"""
Generic JSON → Frappe/ERPNext loader (doctype-aware).

✔ Reads JSON array or JSON-Lines (one object per line)
✔ Each object MUST include "doctype"
✔ Upsert behavior:
   - If "name" exists and matches → update that doc
   - Else if "_match" (filters dict) provided → find & update
   - Else → insert a new doc
✔ Multi-pass retries to satisfy dependencies (parents/links first)
✔ No deletes; idempotent-ish by name/_match

Usage examples:

1) Load a single file:
   bench --site <site> execute repair_portal.repair_portal.scripts.doctype_loader:load_from_file \
         --kwargs "{'json_path': 'apps/repair_portal/repair_portal/scripts/schemas/seed.json'}"

2) Load from default folder (scripts/schemas or ../schemas):
   bench --site <site> execute repair_portal.repair_portal.scripts.doctype_loader:load_from_default_schemas
"""

from __future__ import annotations

import json
import os
import traceback
from typing import Any

import frappe
from frappe.exceptions import DuplicateEntryError, ValidationError

# -------------------------------
# Helpers: site + JSON reading
# -------------------------------


def _ensure_site_context():
	"""Ensure we're connected to a site when called via bench execute."""
	if not getattr(frappe.local, "site", None):
		site = os.environ.get("FRAPPE_SITE") or os.environ.get("SITE_NAME")
		if not site:
			raise RuntimeError(
				"No site context. Use `bench --site <site> execute ...` " "or set FRAPPE_SITE / SITE_NAME."
			)
		frappe.init(site=site)
		frappe.connect()


def _read_json_docs(json_path: str) -> list[dict[str, Any]]:
	with open(json_path, encoding="utf-8") as f:
		raw = f.read().strip()
	if not raw:
		return []

	# Try standard JSON (array or single object)
	try:
		data = json.loads(raw)
		if isinstance(data, dict):
			return [data]
		if isinstance(data, list):
			return data
	except json.JSONDecodeError:
		pass

	# Fallback: JSON Lines (one object per line)
	docs: list[dict[str, Any]] = []
	for ln in raw.splitlines():
		ln = ln.strip().rstrip(",")  # tolerate trailing commas
		if not ln:
			continue
		docs.append(json.loads(ln))
	return docs


# -------------------------------
# Core upsert logic
# -------------------------------

_META_KEYS = {
	"doctype",
	"name",
	"_match",
	# ignore write-protected bookkeeping fields if present
	"owner",
	"creation",
	"modified",
	"modified_by",
	"idx",
}


def _require_doctype(doc: dict[str, Any]) -> str:
	dt = doc.get("doctype")
	if not dt:
		raise ValueError(f"Missing 'doctype' in document: {doc}")
	return dt


def _find_existing_name(doctype: str, doc: dict[str, Any]) -> str | None:
	"""Choose an existing doc to update: by explicit name or by _match filters."""
	if doc.get("name"):
		return doc["name"]

	match = doc.get("_match")
	if isinstance(match, dict) and match:
		found = frappe.get_all(doctype, filters=match, pluck="name", limit=1)
		return found[0] if found else None
	return None


def _update_existing(doctype: str, name: str, payload: dict[str, Any]) -> None:
	"""Apply fields from payload onto an existing doc and save."""
	d = frappe.get_doc(doctype, name)
	for k, v in payload.items():
		if k in _META_KEYS:
			continue
		d.set(k, v)
	d.save(ignore_permissions=True)


def _insert_new(payload: dict[str, Any]) -> str:
	"""Insert a new doc from payload; returns new name."""
	d = frappe.get_doc(payload)
	d.insert(ignore_permissions=True)
	return d.name


def _apply_one(doc: dict[str, Any]) -> bool:
	"""
	Try to apply one doc (insert or update).
	Returns True if applied, False if should retry later (e.g., missing links/parents).
	"""
	doctype = _require_doctype(doc)
	target_name = _find_existing_name(doctype, doc)

	try:
		if target_name and frappe.db.exists(doctype, target_name):
			_update_existing(doctype, target_name, doc)
			print(f"  ↻ updated: {doctype} / {target_name}")
		else:
			try:
				newname = _insert_new(doc)
				print(f"  ✓ created: {doctype} / {newname}")
			except DuplicateEntryError:
				# Another process created it, or name collision → update instead
				name = doc.get("name")
				if name and frappe.db.exists(doctype, name):
					_update_existing(doctype, name, doc)
					print(f"  ↻ updated (after duplicate): {doctype} / {name}")
				else:
					raise
		frappe.db.commit()
		return True

	except ValidationError as e:
		# Typical deferrable errors: parent/link missing, tree constraints, etc.
		frappe.db.rollback()
		print(f"  … deferring (will retry): {doctype} / {target_name or '(new)'} — {e}")
		return False

	except Exception as e:
		frappe.db.rollback()
		print(f"  ✗ error on {doctype} / {target_name or '(new)'}: {e}")
		frappe.log_error(title=f"JSON Loader Error ({doctype})", message=traceback.format_exc())
		# Re-raise to abort the run; comment out if you prefer best-effort
		raise


# -------------------------------
# Batch orchestration
# -------------------------------


def _apply_pass(docs: list[dict[str, Any]]) -> tuple[int, list[dict[str, Any]]]:
	"""Apply one pass; return (applied_count, deferred_docs)."""
	applied = 0
	deferred: list[dict[str, Any]] = []
	for d in docs:
		try:
			ok = _apply_one(d)
			if ok:
				applied += 1
			else:
				deferred.append(d)
		except Exception:
			# fatal for this doc → log & continue best-effort
			# (uncomment `raise` above to abort the whole run)
			continue
	return applied, deferred


# -------------------------------
# Public entry points
# -------------------------------


def load_from_file(json_path: str, max_passes: int = 5) -> None:
	"""
	Load any doctypes from a JSON file where each object includes "doctype".
	"""
	_ensure_site_context()
	path = os.path.abspath(json_path)
	if not os.path.isfile(path):
		raise FileNotFoundError(f"JSON not found: {path}")

	print(f"📄 Loading docs from: {path}")
	docs = _read_json_docs(path)

	# filter: require 'doctype'
	filtered = []
	for d in docs:
		if d.get("doctype"):
			filtered.append(d)
		else:
			print(f"  • skipping doc without 'doctype': {d}")
	if not filtered:
		print("⚠️  No docs with 'doctype' found in file.")
		return

	remaining = filtered[:]
	total_applied = 0

	for p in range(1, max_passes + 1):
		print(f"— pass {p}/{max_passes} —")
		applied, remaining = _apply_pass(remaining)
		total_applied += applied
		print(f"   pass {p}: {applied} applied; {len(remaining)} pending")
		if not remaining:
			break

	print(f"✅ Done. Applied {total_applied} change(s). Pending unresolved: {len(remaining)}")
	if remaining:
		print("   (Likely parent links or validation issues; check console and Error Log.)")


def load_from_folder(folder: str, max_passes: int = 5) -> None:
	"""
	Load from all *.json files in a folder (non-recursive).
	"""
	_ensure_site_context()
	folder = os.path.abspath(folder)
	if not os.path.isdir(folder):
		raise RuntimeError(f"Folder not found: {folder}")

	# collect docs from all files
	from glob import glob

	files = sorted(glob(os.path.join(folder, "*.json")))
	if not files:
		print(f"⚠️  No JSON files in {folder}")
		return

	all_docs: list[dict[str, Any]] = []
	for fpath in files:
		try:
			docs = _read_json_docs(fpath)
			for d in docs:
				if d.get("doctype"):
					all_docs.append(d)
				else:
					print(f"  • skipping (no doctype): {fpath}")
		except Exception as e:
			print(f"  ✗ error reading {fpath}: {e}")

	if not all_docs:
		print("⚠️  No docs with 'doctype' found.")
		return

	print(f"📁 Loading {len(all_docs)} docs from {len(files)} file(s) in {folder}")
	remaining = all_docs[:]
	total_applied = 0

	for p in range(1, max_passes + 1):
		print(f"— pass {p}/{max_passes} —")
		applied, remaining = _apply_pass(remaining)
		total_applied += applied
		print(f"   pass {p}: {applied} applied; {len(remaining)} pending")
		if not remaining:
			break

	print(f"✅ Done. Applied {total_applied} change(s). Pending unresolved: {len(remaining)}")


def load_from_default_schemas(dir_name: str = "schemas", max_passes: int = 5) -> None:
	"""
	Convenience wrapper that looks for schemas under:
	  1) scripts/<dir_name>   (preferred)
	  2) ../<dir_name>        (fallback)
	and loads *all* .json files found (doctype-required per object).
	"""
	_ensure_site_context()
	here = os.path.dirname(os.path.abspath(__file__))
	candidates = [
		os.path.join(here, dir_name),  # scripts/schemas
		os.path.abspath(os.path.join(here, "..", dir_name)),  # ../schemas
	]
	folder = next((p for p in candidates if os.path.isdir(p)), None)
	if not folder:
		raise RuntimeError(
			"No schemas folder found. Tried:\n" f"  - {candidates[0]}\n" f"  - {candidates[1]}"
		)
	print(f"📂 Loading from default schemas: {folder}")
	return load_from_folder(folder, max_passes=max_passes)
