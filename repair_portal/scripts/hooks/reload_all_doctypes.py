#!/usr/bin/env python3
"""
Relative Path: repair_portal/repair_portal/scripts/hooks/reload_all_doctypes.py

Reload all metadata documents in the 'repair_portal' app by finding
.../<module>/<doctype_type>/<docname>/<docname>.json

Counts and prints a per-*Frappe Doctype* summary (DocType, Report, Page, etc.)
with Attempted/Created/Updated/Deferred/Errors.

Run:
  bench --site your_site execute repair_portal.repair_portal.scripts.hooks.reload_all_doctypes:reload_all_doctypes
"""

from __future__ import annotations

import json
import os
from typing import Dict, Iterable, Tuple, Optional

import frappe

# -------------------------------------------------------------------
# Paths (resolved dynamically; no hard-coded bench/app paths)
# -------------------------------------------------------------------

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))                          # .../scripts/hooks
APP_PATH = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))                 # .../repair_portal/repair_portal

# Folder name → Frappe Doctype used for reload_doc and existence checks
TYPE_TO_DOCTYPE = {
    # Frappe core metadata
    "doctype": "DocType",
    "report": "Report",
    "page": "Page",
    "print_format": "Print Format",
    "dashboard_chart": "Dashboard Chart",
    "dashboard_chart_source": "Dashboard Chart Source",
    "workspace": "Workspace",
    "notification": "Notification",
    "role": "Role",
    "server_script": "Server Script",
    "client_script": "Client Script",
    "property_setter": "Property Setter",
    "custom_field": "Custom Field",
    "web_form": "Web Form",
    "web_template": "Web Template",
    "translation": "Translation",
    "workflow": "Workflow",
    "workflow_state": "Workflow State",
    # add others as needed
}

# -------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------

def _log(msg: str) -> None:
    print(msg)
    frappe.logger().info(msg)

def _ensure_site() -> None:
    if not getattr(frappe.local, "site", None):
        site = os.environ.get("FRAPPE_SITE") or os.environ.get("SITE_NAME")
        if not site:
            raise RuntimeError("No site context. Use `bench --site <site> ...` or set FRAPPE_SITE/SITE_NAME.")
        frappe.init(site=site)
        frappe.connect()

def _iter_candidates(app_path: str) -> Iterable[Tuple[str, str, str, str]]:
    """
    Yield (module, doctype_type, docname, json_path) for entries like:
      .../<module>/<doctype_type>/<docname>/<docname>.json
    Only walks directories that look like Frappe metadata.
    """
    for module in os.listdir(app_path):
        mod_path = os.path.join(app_path, module)
        if not os.path.isdir(mod_path) or module.startswith((".", "__")):
            continue

        for doctype_type in os.listdir(mod_path):
            dt_path = os.path.join(mod_path, doctype_type)
            if not os.path.isdir(dt_path) or doctype_type.startswith((".", "__")):
                continue
            if doctype_type not in TYPE_TO_DOCTYPE:
                continue

            for docname in os.listdir(dt_path):
                dn_path = os.path.join(dt_path, docname)
                if not os.path.isdir(dn_path) or docname.startswith((".", "__")):
                    continue
                json_path = os.path.join(dn_path, f"{docname}.json")
                if os.path.isfile(json_path):
                    yield (module, doctype_type, docname, json_path)

def _read_meta(json_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Read just enough from a metadata JSON to know:
      - meta_doctype (e.g., "DocType", "Report")
      - meta_name    (the record's name)
    If unreadable, return (None, None) and let reload_doc handle it.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None, None

    # Files are single dict for metadata; if it's a list, take first dict-like
    if isinstance(data, list):
        for x in data:
            if isinstance(x, dict):
                data = x
                break

    if not isinstance(data, dict):
        return None, None

    meta_doctype = data.get("doctype")
    meta_name = data.get("name")

    # Some metadata store the user-facing label separately; but for metadata JSON,
    # "name" is typically the primary key (e.g., DocType name, Report name, etc.)
    if not isinstance(meta_doctype, str):
        meta_doctype = None
    if not isinstance(meta_name, str):
        meta_name = None

    return meta_doctype, meta_name

def _pre_exists(doctype: str, name: str) -> bool:
    try:
        return bool(frappe.db.exists(doctype, name))
    except Exception:
        return False

def _sanitize_workflow_json(json_path: str) -> None:
    """
    Convert list-valued fields in Workflow definitions into newline-separated strings,
    matching what Frappe expects in those fields.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        _log(f"⚠️  Could not parse JSON in {json_path}: {e}")
        return

    changed = False
    items = [data] if isinstance(data, dict) else (data if isinstance(data, list) else [])
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("doctype") in {"Workflow", "Workflow State"}:
            # states
            for st in item.get("states", []) or []:
                if isinstance(st.get("only_allow_edit_for"), list):
                    st["only_allow_edit_for"] = "\n".join(st["only_allow_edit_for"])
                    changed = True
            # transitions
            for tr in item.get("transitions", []) or []:
                if isinstance(tr.get("allowed"), list):
                    tr["allowed"] = "\n".join(tr["allowed"])
                    changed = True

    if changed:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        _log(f"✅ Sanitized workflow file: {json_path}")

# -------------------------------------------------------------------
# Summary table
# -------------------------------------------------------------------

def _print_summary_table(stats_by_type: Dict[str, Dict[str, int]], totals: Dict[str, int]) -> None:
    total_attempts = sum(v["attempted"] for v in stats_by_type.values())
    print(
        f"\n✅ Done. Applied {totals['created'] + totals['updated']} change(s). "
        f"(created={totals['created']}, updated={totals['updated']}, "
        f"deferred={totals['deferred']}, errors={totals['errors']})\n"
    )
    print(f"All {total_attempts} reload attempts completed.\n")

    name_col = max(4, *(len(k) for k in stats_by_type.keys()), len("TOTAL")) if stats_by_type else 10
    def w(vals, minw): return max(minw, *(len(str(v)) for v in vals)) if stats_by_type else minw

    attempted_w = w((v["attempted"] for v in stats_by_type.values()), 9)
    created_w   = w((v["created"]   for v in stats_by_type.values()), 7)
    updated_w   = w((v["updated"]   for v in stats_by_type.values()), 7)
    deferred_w  = w((v["deferred"]  for v in stats_by_type.values()), 8)
    errors_w    = w((v["errors"]    for v in stats_by_type.values()), 6)

    header = (
        f"{'Type'.ljust(name_col)}  "
        f"{'Attempted'.rjust(attempted_w)}  "
        f"{'Created'.rjust(created_w)}  "
        f"{'Updated'.rjust(updated_w)}  "
        f"{'Deferred'.rjust(deferred_w)}  "
        f"{'Errors'.rjust(errors_w)}"
    )
    print(header)
    print("-" * len(header))

    tot_attempt = tot_created = tot_updated = tot_deferred = tot_errors = 0

    for dt in sorted(stats_by_type.keys()):
        row = stats_by_type[dt]
        tot_attempt  += row["attempted"]
        tot_created  += row["created"]
        tot_updated  += row["updated"]
        tot_deferred += row["deferred"]
        tot_errors   += row["errors"]

        print(
            f"{dt.ljust(name_col)}  "
            f"{str(row['attempted']).rjust(attempted_w)}  "
            f"{str(row['created']).rjust(created_w)}  "
            f"{str(row['updated']).rjust(updated_w)}  "
            f"{str(row['deferred']).rjust(deferred_w)}  "
            f"{str(row['errors']).rjust(errors_w)}"
        )

    print("-" * len(header))
    print(
        f"{'TOTAL'.ljust(name_col)}  "
        f"{str(tot_attempt).rjust(attempted_w)}  "
        f"{str(tot_created).rjust(created_w)}  "
        f"{str(tot_updated).rjust(updated_w)}  "
        f"{str(tot_deferred).rjust(deferred_w)}  "
        f"{str(tot_errors).rjust(errors_w)}"
    )
    print("")

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def reload_all_doctypes() -> None:
    """
    Read each metadata JSON, determine its actual doctype/name, then reload with frappe.reload_doc.
    Count Created/Updated using a before/after existence check on the actual doctype+name.
    """
    _ensure_site()
    _log("🔄 Reloading all metadata in repair_portal...")

    # Per *Frappe Doctype* stats (DocType, Report, Page, etc.)
    stats_by_type: Dict[str, Dict[str, int]] = {}
    totals = {"created": 0, "updated": 0, "deferred": 0, "errors": 0}

    def bump(dt: str, key: str) -> None:
        row = stats_by_type.setdefault(dt, {"attempted": 0, "created": 0, "updated": 0, "deferred": 0, "errors": 0})
        row[key] += 1

    for module, doctype_type, docname, json_path in _iter_candidates(APP_PATH):
        # Read actual metadata info for correct grouping and existence checks
        meta_doctype, meta_name = _read_meta(json_path)
        # Fallbacks if JSON is odd: use folder-based mapping and docname
        display_doctype = meta_doctype or TYPE_TO_DOCTYPE.get(doctype_type, doctype_type)
        exists_check_dt = meta_doctype or TYPE_TO_DOCTYPE.get(doctype_type, doctype_type)
        target_name = meta_name or docname

        bump(display_doctype, "attempted")

        # Pre-existence (accurate Created/Updated split uses before+after)
        existed_before = _pre_exists(exists_check_dt, target_name)

        # Workflow sanitizer
        if doctype_type == "workflow":
            _sanitize_workflow_json(json_path)

        try:
            # Use folder doctype_type for reload_doc (this is how Frappe locates the file)
            frappe.reload_doc(module, doctype_type, docname, force=True)

            # After reload, re-check for accurate Created signal
            existed_after = _pre_exists(exists_check_dt, target_name)

            if existed_before and existed_after:
                bump(display_doctype, "updated")
                totals["updated"] += 1
            elif (not existed_before) and existed_after:
                bump(display_doctype, "created")
                totals["created"] += 1
            else:
                # Reload succeeded but DB record not present (rare edge, count as updated)
                bump(display_doctype, "updated")
                totals["updated"] += 1

        except frappe.ValidationError as e:
            bump(display_doctype, "deferred")
            totals["deferred"] += 1
            _log(f"… deferred {module}/{doctype_type}/{docname}: {e}")

        except Exception as e:
            bump(display_doctype, "errors")
            totals["errors"] += 1
            _log(f"❌ Error reloading {module}/{doctype_type}/{docname}: {e}  🔹 File: {json_path}")
            frappe.logger().error("reload_doc error", exc_info=True)

    _print_summary_table(stats_by_type, totals)


if __name__ == "__main__":
    reload_all_doctypes()
