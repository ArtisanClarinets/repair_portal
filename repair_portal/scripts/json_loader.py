# repair_portal/repair_portal/scripts/json_loader.py
from __future__ import annotations
import json
import os
from typing import Dict, Any, List, Optional

import frappe
from frappe.exceptions import DuplicateEntryError


# ──────────────────────────────────────────────────────────────────────────────
# Path helpers
# ──────────────────────────────────────────────────────────────────────────────

def _module_dir() -> str:
    """Directory of this file: .../your_app/your_app/scripts"""
    return os.path.dirname(os.path.abspath(__file__))

def _schemas_dir(spec: str) -> str:
    """Resolve the schemas directory.

    Priority:
      1) If `spec` is an absolute path → use it.
      2) Relative to scripts/ → scripts/<spec>      (e.g. scripts/schemas)  ← default layout
      3) Sibling to scripts/ → ../<spec>            (e.g. ../schemas)       ← fallback

    Returns the first existing directory; otherwise returns the preferred
    path (scripts/<spec>) so the error message is helpful.
    """
    if os.path.isabs(spec):
        return spec

    scripts_dir = _module_dir()
    preferred = os.path.abspath(os.path.join(scripts_dir, spec))           # scripts/<spec>
    sibling   = os.path.abspath(os.path.join(scripts_dir, "..", spec))     # ../<spec>

    if os.path.isdir(preferred):
        return preferred
    if os.path.isdir(sibling):
        return sibling
    return preferred  # not found; return preferred so error message points here


# ──────────────────────────────────────────────────────────────────────────────
# JSON parsing helpers
# ──────────────────────────────────────────────────────────────────────────────

def _is_json_lines(text: str) -> bool:
    s = text.lstrip()
    # Not starting with '[' means likely JSONL or a single object
    return not s.startswith("[")

def _read_docs_from_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
        if not raw:
            return []

        if _is_json_lines(raw):
            # JSON Lines or a single object
            docs = []
            for ln in raw.splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                docs.append(json.loads(ln))
            return docs
        else:
            data = json.loads(raw)
            if isinstance(data, dict):
                return [data]
            if isinstance(data, list):
                return data
            raise ValueError(f"Unsupported JSON root in {path}: {type(data)}")

def _doctype_from_filename(filename: str) -> str:
    # "Item Group.json" → "Item Group"
    base = os.path.splitext(os.path.basename(filename))[0]
    return base

def _ensure_doctype(doc: Dict[str, Any], default_doctype: str) -> Dict[str, Any]:
    if "doctype" not in doc or not doc["doctype"]:
        doc["doctype"] = default_doctype
    return doc


# ──────────────────────────────────────────────────────────────────────────────
# Upsert helpers (non-destructive)
# ──────────────────────────────────────────────────────────────────────────────

def _update_existing(doctype: str, name: str, payload: Dict[str, Any]) -> None:
    existing = frappe.get_doc(doctype, name)
    for k, v in payload.items():
        if k in ("doctype", "name"):
            continue
        existing.set(k, v)
    existing.save(ignore_permissions=True)

def _insert_new(payload: Dict[str, Any]) -> Optional[str]:
    try:
        d = frappe.get_doc(payload)
        d.insert(ignore_permissions=True)
        return d.name
    except DuplicateEntryError:
        # Name collision / already created elsewhere → update instead
        name = payload.get("name")
        if name:
            _update_existing(payload["doctype"], name, payload)
            return name
        return None

def _find_match_name(doctype: str, doc: Dict[str, Any]) -> Optional[str]:
    """
    Matching strategy:
      1) If 'name' present → use it.
      2) If '_match' (filters dict) provided → find existing by those filters.
      3) Else, no match (will insert).
    """
    if doc.get("name"):
        return doc["name"]

    match = doc.get("_match")
    if isinstance(match, dict) and match:
        res = frappe.get_all(doctype, filters=match, pluck="name", limit=1)
        return res[0] if res else None
    return None

def _try_apply(doc: Dict[str, Any]) -> bool:
    """
    Attempt one upsert of a single document.
    Returns True if applied, False if should retry later (e.g., parent missing).
    """
    doctype = doc["doctype"]
    name_to_update = _find_match_name(doctype, doc)

    try:
        if name_to_update and frappe.db.exists(doctype, name_to_update):
            _update_existing(doctype, name_to_update, doc)
        else:
            _insert_new(doc)
        frappe.db.commit()
        return True
    except frappe.ValidationError:
        # Typical for tree parents missing or linked refs not ready yet → retry later
        frappe.db.rollback()
        return False
    except Exception:
        frappe.db.rollback()
        raise


# ──────────────────────────────────────────────────────────────────────────────
# Batch pass
# ──────────────────────────────────────────────────────────────────────────────

def _load_files_in_pass(files: List[str]) -> int:
    """
    Make a pass over all files; returns count of docs successfully applied in this pass.
    """
    applied = 0
    for path in files:
        default_doctype = _doctype_from_filename(path)
        docs = _read_docs_from_file(path)
        for d in docs:
            _ensure_doctype(d, default_doctype)

        pending: List[Dict[str, Any]] = docs[:]
        next_round: List[Dict[str, Any]] = []
        for doc in pending:
            ok = _try_apply(doc)
            if ok:
                applied += 1
            else:
                next_round.append(doc)
        # Remaining docs will be retried on subsequent global passes
    return applied


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def load_from_adjacent(directory: str = "schemas", max_passes: int = 5) -> None:
    """
    Load JSON schemas from a directory *relative to this scripts/ folder* by default.

    Defaults:
      - directory="schemas"  → resolved to  scripts/schemas     (preferred)
                               and falls back to ../schemas     (sibling to scripts)
      - You may also pass an absolute path.

    Example:
      bench --site <yoursite> execute repair_portal.repair_portal.scripts.json_loader:load_from_adjacent \
            --kwargs "{'directory': 'schemas'}"
    """
    # Ensure site context if invoked outside hooks
    if not getattr(frappe.local, "site", None):
        site = os.environ.get("FRAPPE_SITE") or os.environ.get("SITE_NAME")
        if not site:
            raise RuntimeError("No site context. Use `bench --site <site> execute ...` or set FRAPPE_SITE.")
        frappe.init(site=site)
        frappe.connect()

    path = _schemas_dir(directory)
    if not os.path.isdir(path):
        scripts_dir = _module_dir()
        preferred = os.path.abspath(os.path.join(scripts_dir, directory))      # scripts/<directory>
        sibling   = os.path.abspath(os.path.join(scripts_dir, "..", directory))# ../<directory>
        raise RuntimeError(
            "Schemas directory not found.\n"
            f"  Tried: {preferred}\n"
            f"         {sibling}\n"
            "Create one of these or pass an absolute path / correct directory argument."
        )

    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".json")]
    if not files:
        frappe.logger().info(f"No JSON files in {path}")
        return

    # Multi-pass to satisfy dependencies (parents, linked docs, etc.)
    total_applied = 0
    for _ in range(max_passes):
        applied = _load_files_in_pass(files)
        total_applied += applied
        if applied == 0:
            break

    frappe.logger().info(
        f"JSON Loader finished. Applied {total_applied} changes in up to {max_passes} passes from {path}."
    )
#############################################################################
