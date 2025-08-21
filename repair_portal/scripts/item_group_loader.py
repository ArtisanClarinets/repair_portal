# repair_portal/repair_portal/scripts/item_group_loader.py
"""
Item Group loader: create/update Item Groups from a JSON file.

Accepts either:
  - a JSON array: [ { ... }, { ... } ]
  - JSON Lines: one JSON object per line

Each object may include:
  - name (string)                      # treated as the Item Group name
  - parent_item_group (string)         # default: "All Item Groups"
  - is_group (0/1 or true/false)       # default: 0
  - doctype (optional, ignored unless "Item Group")

Idempotent: If the Item Group already exists, it's updated. Nothing is deleted.
"""

from __future__ import annotations

import json
import os
import traceback
from typing import Any

import frappe
from frappe.exceptions import ValidationError

# -------------------------------
# Helpers: site + JSON reading
# -------------------------------


def _ensure_site_context():
	"""Make sure we're connected to a Frappe site if called via bench execute."""
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

	# Try standard JSON first (array or single object)
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


def _as_int01(v: Any) -> int:
	if isinstance(v, bool):
		return 1 if v else 0
	try:
		return 1 if int(v) else 0
	except Exception:
		return 0


def _normalize(doc: dict[str, Any]) -> dict[str, Any]:
	"""Map incoming fields to Item Group model."""
	# Only accept Item Group docs or docs without doctype (assume Item Group).
	if doc.get("doctype") and doc["doctype"] != "Item Group":
		raise ValueError(f"Skipping non-Item Group doc with doctype={doc['doctype']}")

	name = doc.get("name") or doc.get("item_group_name")
	if not name:
		raise ValueError("Each object needs at least a 'name' (or 'item_group_name').")

	parent = doc.get("parent_item_group") or "All Item Groups"
	is_group = _as_int01(doc.get("is_group", 0))

	return {
		"doctype": "Item Group",
		"name": name,  # safe for update path; on insert, Frappe will set from item_group_name
		"item_group_name": name,
		"parent_item_group": parent,
		"is_group": is_group,
	}


def _insert_or_update(row: dict[str, Any]) -> bool:
	"""
	Returns True if applied, False if we should retry (e.g., parent missing).
	"""
	data = _normalize(row)
	name = data["name"]

	try:
		if frappe.db.exists("Item Group", name):
			ig = frappe.get_doc("Item Group", name)
			# Update mutable fields
			ig.item_group_name = data["item_group_name"]
			ig.parent_item_group = data["parent_item_group"]
			ig.is_group = data["is_group"]
			ig.save(ignore_permissions=True)
			print(f"  ↻ updated: {name}")
		else:
			ig = frappe.get_doc(data)
			ig.insert(ignore_permissions=True)
			print(f"  ✓ created: {ig.name}")
		frappe.db.commit()
		return True
	except ValidationError as e:
		# Most common causes:
		# - parent_item_group doesn't exist yet
		# - trying to set is_group=0 while it has children
		frappe.db.rollback()
		print(f"  … deferring (will retry): {name}  —  {e}")
		return False
	except Exception as e:
		frappe.db.rollback()
		print(f"  ✗ error on '{name}': {e}")
		frappe.log_error(title="Item Group Loader Error", message=traceback.format_exc())
		# Reraise to abort the run; comment the next line if you prefer best-effort
		raise


# -------------------------------
# Public entry points
# -------------------------------


def load_item_groups_from_file(json_path: str, max_passes: int = 5) -> None:
	"""
    Load Item Groups from a JSON file.
    Usage:
      bench --site <yoursite> execute repair_portal.repair_portal.scripts.item_group_loader:load_item_groups_from_file \
            --kwargs "{'json_path': '/absolute/or/relative/path/to/item_groups.json'}"
    """
	_ensure_site_context()
	path = os.path.abspath(json_path)
	if not os.path.isfile(path):
		raise FileNotFoundError(f"JSON not found: {path}")

	print(f"📄 Loading Item Groups from: {path}")
	docs = _read_json_docs(path)

	# Filter only Item Group docs (or those without doctype)
	filtered: list[dict[str, Any]] = []
	for d in docs:
		dt = d.get("doctype")
		if dt in (None, "Item Group"):
			filtered.append(d)
		else:
			print(f"  • skipping non-Item Group doc (doctype={dt})")

	if not filtered:
		print("⚠️  No Item Group docs found in file.")
		return

	remaining = filtered[:]
	total_applied = 0

	for p in range(1, max_passes + 1):
		print(f"— pass {p}/{max_passes} —")
		next_round: list[dict[str, Any]] = []
		applied_this_pass = 0

		for row in remaining:
			ok = _insert_or_update(row)
			if ok:
				applied_this_pass += 1
			else:
				next_round.append(row)

		total_applied += applied_this_pass
		print(f"   pass {p}: {applied_this_pass} applied; {len(next_round)} pending")

		if not next_round:
			break
		remaining = next_round

	print(f"✅ Done. Applied {total_applied} change(s). Pending unresolved: {len(remaining)}")
	if remaining:
		print("   (Likely parent groups missing or validation issues; check console and Error Log.)")


def load_item_groups_from_default_schemas(dir_name: str = "schemas", filename_hint: str = "") -> None:
	"""
	Convenience wrapper that looks for JSON under:
	  1) scripts/<dir_name>   (preferred)
	  2) ../<dir_name>        (fallback)

	It loads the first matching file:
	  - exact "Item Group.json", else
	  - any file containing "item_group" (case-insensitive), else
	  - all *.json in the folder (filtering to Item Group docs)

	Usage:
	  bench --site <yoursite> execute repair_portal.repair_portal.scripts.item_group_loader:load_item_groups_from_default_schemas
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

	# Prioritize common names
	preferred = [
		os.path.join(folder, "Item Group.json"),
		os.path.join(folder, "item_group.json"),
		os.path.join(folder, "item_groups.json"),
	]
	if filename_hint:
		preferred.insert(0, os.path.join(folder, filename_hint))

	for p in preferred:
		if os.path.isfile(p):
			return load_item_groups_from_file(p)

	# Fallback: use first *.json
	from glob import glob

	json_files = sorted(glob(os.path.join(folder, "*.json")))
	if not json_files:
		print(f"⚠️  No JSON files in {folder}")
		return

	# Try each until one has Item Group docs
	for p in json_files:
		try:
			print(f"Trying: {p}")
			return load_item_groups_from_file(p)
		except Exception as e:
			# keep trying others; log and move on
			print(f"   skipping {p}: {e}")

	print("⚠️  No usable Item Group data found in any JSON file.")
