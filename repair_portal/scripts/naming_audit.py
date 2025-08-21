# repair_portal/repair_portal/scripts/naming_audit.py
# Execution: bench execute repair_portal.install.audit_naming_series_after_migrate
#
#

from __future__ import annotations

import json
import os
import re
import traceback
from glob import glob

import frappe

# Optional: use your app logger if installed
try:
	from repair_portal.logger import get_logger

	log = get_logger("naming_audit")
except Exception:
	log = None

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../repair_portal/repair_portal
APP_DIR = os.path.dirname(APP_ROOT)  # .../repair_portal
SEARCH_GLOB = os.path.join(
	APP_ROOT, "**", "doctype", "*", "*.json"
)  # include workflow json too; we'll filter

FORMAT_PLACEHOLDER_RE = re.compile(r"\{([A-Za-z0-9_]+)\}")


def _ensure_site():
	if not getattr(frappe.local, "site", None):
		site = os.environ.get("FRAPPE_SITE") or os.environ.get("SITE_NAME")
		if not site:
			raise RuntimeError("No site context. Use `bench --site <site> execute ...` or set FRAPPE_SITE.")
		frappe.init(site=site)
		frappe.connect()


def _read_json(p: str) -> dict:
	with open(p, encoding="utf-8") as f:
		return json.load(f)


def _controller_path(json_path: str) -> str | None:
	# …/doctype/My DocType/My DocType.json → …/doctype/My DocType/My DocType.py
	base, filename = os.path.split(json_path)
	name, _ = os.path.splitext(filename)
	py_path = os.path.join(base, f"{name}.py")
	return py_path if os.path.isfile(py_path) else None


def _controller_has_autoname(py_path: str) -> bool:
	try:
		with open(py_path, encoding="utf-8") as f:
			src = f.read()
		return "def autoname(" in src
	except Exception:
		return False


def _strip(s: str | None) -> str:
	return (s or "").strip()


def _format_placeholders(autoname: str) -> list[str]:
	return FORMAT_PLACEHOLDER_RE.findall(autoname or "")


def _warn(msg: str):
	print(f"⚠️  {msg}")
	if log:
		log.warning(msg)


def _err(msg: str):
	print(f"\033[91m✗ {msg}\033[0m")
	if log:
		log.error(msg)


def _ok(msg: str):
	print(f"✓ {msg}")
	if log:
		log.info(msg)


def _audit_doc(json_path: str) -> tuple[str, str, list[str]]:
	"""
	Returns: (doctype, autoname_display, warnings)
	"""
	data = _read_json(json_path)
	if data.get("doctype") != "DocType":
		return "", "", []  # ignore workflow/print format schemas

	doctype = data.get("name") or os.path.basename(os.path.dirname(json_path))
	autoname = _strip(data.get("autoname"))

	warnings: list[str] = []
	notes: list[str] = []

	py = _controller_path(json_path)
	has_controller_autoname = _controller_has_autoname(py) if py else False

	if not autoname and not has_controller_autoname:
		notes.append("no autoname (manual or name set elsewhere)")
	else:
		if has_controller_autoname and autoname:
			warnings.append(
				"JSON 'autoname' present AND controller 'autoname' defined — controller takes precedence"
			)

		if autoname:
			# Style normalization
			if autoname.startswith("format:"):
				pattern = autoname[len("format:") :]
				if pattern.startswith(" "):
					warnings.append("leading space after 'format:'")
				if pattern.endswith(" ") or pattern.endswith("."):
					warnings.append("trailing space/dot in format")
				# check placeholders exist
				fields = _format_placeholders(autoname)
				try:
					meta = frappe.get_meta(doctype)
					fieldnames = {f.fieldname for f in meta.fields}
					for fld in fields:
						if fld not in fieldnames and fld not in {"YY", "YYYY", "MM", "DD"}:
							warnings.append(f"format placeholder '{{{fld}}}' not a field in DocType")
				except Exception as e:
					warnings.append(f"meta lookup failed: {e}")
			elif autoname.startswith("field:"):
				fld = autoname[len("field:") :]
				try:
					meta = frappe.get_meta(doctype)
					df = next((f for f in meta.fields if f.fieldname == fld), None)
					if not df:
						warnings.append(f"field '{fld}' not found in DocType")
					else:
						if not getattr(df, "unique", 0):
							warnings.append(f"field '{fld}' is not Unique (duplicate saves will fail)")
				except Exception as e:
					warnings.append(f"meta lookup failed: {e}")
			elif autoname.startswith("naming_series:"):
				# Ensure DocType has naming_series field or standard support
				try:
					meta = frappe.get_meta(doctype)
					ns_field = next((f for f in meta.fields if f.fieldname == "naming_series"), None)
					if not ns_field:
						warnings.append("uses naming_series but DocType lacks a 'naming_series' field")
				except Exception as e:
					warnings.append(f"meta lookup failed: {e}")
			elif autoname in {"hash", "prompt"}:
				pass  # ok
			else:
				# legacy pattern like "OPRT-.#####"
				warnings.append("legacy/implicit pattern; prefer 'format:' (e.g., format:OPRT-{#####})")

	# Compose display text
	disp = autoname or ("controller.autoname" if has_controller_autoname else "—")

	# Emit line
	print(f"\n• {doctype}")
	print(f"  - json_path: {json_path}")
	if py:
		print(f"  - controller: {py}  ({'autoname' if has_controller_autoname else '—'})")
	print(f"  - autoname: {disp}")
	for w in warnings:
		_warn(f"{doctype}: {w}")
	for n in notes:
		_ok(f"{doctype}: {n}")

	return doctype, disp, warnings


def run():
	_ensure_site()
	json_files = sorted(glob(SEARCH_GLOB, recursive=True))
	if not json_files:
		print("No DocType JSON files found.")
		return

	print(f"Scanning {len(json_files)} JSON files under {APP_ROOT} …")

	issues = 0
	reviewed = 0
	for p in json_files:
		try:
			dt, disp, warns = _audit_doc(p)
			if dt:
				reviewed += 1
				issues += len(warns)
		except Exception as e:
			_err(f"Failed auditing {p}: {e}")
			traceback.print_exc()

	print("\n──────────── Summary ────────────")
	print(f"Reviewed doctypes: {reviewed}")
	print(f"Issues flagged   : {issues}")
	if issues == 0:
		print("All good ✅")


# bench --site <site> execute repair_portal.repair_portal.scripts.naming_audit:run
def main():
	run()
