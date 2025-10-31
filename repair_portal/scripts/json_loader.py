# repair_portal/repair_portal/scripts/reload_all_doctypes.py
# Date: 2025-10-31
# Version: 0.1.1
# Description: JSON/JSONL loader for Doctype schemas; insert-or-update helper with type-safe returns.
# Dependencies: frappe, typing

from __future__ import annotations

import json
import os
from typing import Any, Iterable, cast

import frappe
from frappe.exceptions import DuplicateEntryError, ValidationError


# ──────────────────────────────────────────────────────────────────────────────
# Path helpers
# ──────────────────────────────────────────────────────────────────────────────

def _module_dir() -> str:
    # .../repair_portal/repair_portal/scripts
    return os.path.dirname(os.path.abspath(__file__))


def _resolve_base_dir(spec: str) -> str:
    """
    Resolve the schemas directory.

    Priority:
      1) Absolute path → use it as-is
      2) scripts/<spec> (preferred)
      3) ../<spec> (fallback, sibling to scripts)

    Returns the first existing directory; otherwise returns the preferred path
    so that any error message points somewhere helpful.
    """
    if os.path.isabs(spec):
        return spec

    scripts_dir = _module_dir()
    preferred = os.path.abspath(os.path.join(scripts_dir, spec))
    sibling = os.path.abspath(os.path.join(scripts_dir, "..", spec))

    if os.path.isdir(preferred):
        return preferred
    if os.path.isdir(sibling):
        return sibling
    return preferred  # not found; we’ll raise later with a clear message


# ──────────────────────────────────────────────────────────────────────────────
# JSON helpers
# ──────────────────────────────────────────────────────────────────────────────

def _is_json_lines(text: str) -> bool:
    s = text.lstrip()
    return not s.startswith("[")


def _read_docs_from_file(path: str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        raw = f.read().strip()
    if not raw:
        return []

    if _is_json_lines(raw):
        docs: list[dict[str, Any]] = []
        for ln in raw.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            docs.append(json.loads(ln))
        return docs

    data = json.loads(raw)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported JSON root in {path}: {type(data)}")


def _doctype_from_filename(filename: str) -> str:
    # "Item Group.json" → "Item Group"
    return os.path.splitext(os.path.basename(filename))[0]


def _ensure_doctype(doc: dict[str, Any], default_doctype: str) -> dict[str, Any]:
    if not doc.get("doctype"):
        doc["doctype"] = default_doctype
    return doc


# ──────────────────────────────────────────────────────────────────────────────
# DB helpers
# ──────────────────────────────────────────────────────────────────────────────

def _exception_is_duplicate(err: BaseException) -> bool:
    """
    Return True if `err` represents a duplicate/unique key collision.
    We’re defensive here to cover MariaDB/MySQL IntegrityError(1062) surfaced
    through different layers, or Frappe's DuplicateEntryError.
    """
    if isinstance(err, DuplicateEntryError):
        return True

    s = repr(err)
    # Common patterns:
    # - "IntegrityError(1062, "Duplicate entry 'XYZ' for key 'PRIMARY'")"
    # - "Duplicate entry" in message text from DB-API wrappers
    return ("1062" in s and "Duplicate entry" in s) or ("Duplicate entry" in s)


def _find_match_name(doctype: str, doc: dict[str, Any]) -> str | None:
    """
    Matching strategy:
      1) If 'name' is present → use it.
      2) If '_match' (filters dict) is present → query for an existing name.
      3) Else → None (caller may attempt insert).
    """
    if doc.get("name"):
        return doc["name"]

    match = doc.get("_match")
    if isinstance(match, dict) and match:
        res = frappe.get_all(doctype, filters=match, pluck="name", limit=1)
        return res[0] if res else None
    return None


def _update_existing(doctype: str, name: str, payload: dict[str, Any]) -> None:
    doc = frappe.get_doc(doctype, name)
    for k, v in payload.items():
        if k in {"doctype", "name"}:
            continue
        doc.set(k, v)
    doc.save(ignore_permissions=True)


def _insert_or_update(payload: dict[str, Any]) -> str:
    """
    Insert the given payload. If we hit a duplicate/unique collision, treat it
    as 'update existing'. Returns the final document name.
    """
    try:
        d = frappe.get_doc(payload)
        d.insert(ignore_permissions=True)
        # Defensive: ensure the inserted doc has a name; cast for static typing.
        if not getattr(d, "name", None):
            raise RuntimeError(f"Inserted document has no name: doctype={payload.get('doctype')}")
        return cast(str, d.name)
    except Exception as e:
        if _exception_is_duplicate(e):
            # Resolve target name (explicit name or via _match).
            doctype = payload["doctype"]
            name = payload.get("name") or _find_match_name(doctype, payload)
            if not name:
                # Fallback: try to infer by a few common natural keys if present.
                # (safe no-op if fields not present)
                natural_keys = ["title", "item_code", "brand", "abbr"]
                for key in natural_keys:
                    if payload.get(key):
                        found = frappe.get_all(doctype, filters={key: payload[key]}, pluck="name", limit=1)
                        if found:
                            name = found[0]
                            break
            if not name:
                # As a last resort, if the DB says duplicate, the 'name' already exists.
                # Try using payload['name'] if the doctype uses 'name' as the natural key.
                name = payload.get("name")

            if not name:
                # We really can’t identify the target to update — bubble up as a real error.
                raise

            _update_existing(doctype, name, payload)
            return name
        # Not a duplicate → real error.
        raise


def _apply_one(doc: dict[str, Any]) -> bool:
    """
    Try to apply one document (insert-or-update).
    Returns:
      True  → applied successfully
      False → soft failure that may succeed on a later pass (e.g., ValidationError due to missing parent/link)
    """
    try:
        target_name = _find_match_name(doc["doctype"], doc) or doc.get("name")
        if target_name and frappe.db.exists(doc["doctype"], target_name):
            _update_existing(doc["doctype"], target_name, doc)
        else:
            _insert_or_update(doc)

        frappe.db.commit()
        return True
    except ValidationError:
        # Usually indicates unmet dependencies (tree parent or linked row not ready yet).
        frappe.db.rollback()
        return False
    except Exception:
        frappe.db.rollback()
        raise


# ──────────────────────────────────────────────────────────────────────────────
# Batch loader
# ──────────────────────────────────────────────────────────────────────────────

def _iter_json_files(base_dir: str) -> Iterable[str]:
    for entry in sorted(os.listdir(base_dir)):
        if entry.lower().endswith(".json"):
            yield os.path.join(base_dir, entry)


def _load_file(path: str) -> tuple[int, list[dict[str, Any]]]:
    """
    Returns (applied_count, leftover_docs)
    """
    default_doctype = _doctype_from_filename(path)
    docs = [_ensure_doctype(d, default_doctype) for d in _read_docs_from_file(path)]

    applied = 0
    leftovers: list[dict[str, Any]] = []

    for d in docs:
        ok = _apply_one(d)
        if ok:
            applied += 1
        else:
            leftovers.append(d)

    return applied, leftovers


def _load_all_files_in_pass(files: list[str]) -> tuple[int, dict[str, list[dict[str, Any]]]]:
    """
    Make one pass over all files.

    Returns:
      (applied_count, pending_by_file)
      where pending_by_file maps path → list of doc payloads that should be retried.
    """
    total_applied = 0
    pending_by_file: dict[str, list[dict[str, Any]]] = {}

    for path in files:
        applied, leftovers = _load_file(path)
        total_applied += applied
        if leftovers:
            pending_by_file[path] = leftovers

    return total_applied, pending_by_file


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def reload_all_doctypes(directory: str = "schemas", max_passes: int = 5, verbose: bool = True) -> None:
    """
    Reload all doctypes from JSON/JSONL files in a directory adjacent to this scripts/ folder by default.

    - Duplicate key / unique collisions are treated as 'update' (no error).
    - Multiple passes are performed to satisfy parent/linked dependencies.
    - Only emits/raises for *real* errors (documents that cannot be applied after all passes).

    Example:
      bench --site <site> execute repair_portal.repair_portal.scripts.reload_all_doctypes:reload_all_doctypes \
            --kwargs "{'directory': 'schemas'}"
    """
    # Ensure site context if invoked outside hooks
    if not getattr(frappe.local, "site", None):
        site = os.environ.get("FRAPPE_SITE") or os.environ.get("SITE_NAME")
        if not site:
            raise RuntimeError("No site context. Use `bench --site <site> execute ...` or set FRAPPE_SITE.")
        frappe.init(site=site)
        frappe.connect()

    base_dir = _resolve_base_dir(directory)
    if not os.path.isdir(base_dir):
        scripts_dir = _module_dir()
        preferred = os.path.abspath(os.path.join(scripts_dir, directory))
        sibling = os.path.abspath(os.path.join(scripts_dir, "..", directory))
        raise RuntimeError(
            "Schemas directory not found.\n"
            f"  Tried: {preferred}\n"
            f"         {sibling}\n"
            "Create one of these or pass an absolute path / correct directory argument."
        )

    files = list(_iter_json_files(base_dir))
    if not files:
        frappe.logger().info(f"[reload_all_doctypes] No JSON files in {base_dir}")
        return

    # Keep per-file pending docs for retries across passes
    pending_by_file: dict[str, list[dict[str, Any]]] = {}

    total_applied = 0
    for pass_no in range(1, max_passes + 1):
        if verbose:
            frappe.logger().info(f"[reload_all_doctypes] Pass {pass_no}/{max_passes}")

        # If we have pending docs, write them to temp in-memory map and process these first.
        # We do it by replacing the per-file load logic where we short-circuit to applying pending payloads.
        applied_this_pass = 0
        new_pending: dict[str, list[dict[str, Any]]] = {}

        for path in files:
            if path in pending_by_file:
                docs = pending_by_file[path]
                applied, leftovers = 0, []
                for d in docs:
                    ok = _apply_one(d)
                    if ok:
                        applied += 1
                    else:
                        leftovers.append(d)
                applied_this_pass += applied
                if leftovers:
                    new_pending[path] = leftovers
            else:
                applied, leftovers = _load_file(path)
                applied_this_pass += applied
                if leftovers:
                    new_pending[path] = leftovers

        total_applied += applied_this_pass
        pending_by_file = new_pending

        if verbose:
            frappe.logger().info(
                f"[reload_all_doctypes] Pass {pass_no} applied {applied_this_pass} change(s); "
                f"{sum(len(v) for v in pending_by_file.values())} pending."
            )

        if applied_this_pass == 0:
            break

    # After all passes, anything left is a real error
    if pending_by_file:
        # Collect diagnostic info without spamming tracebacks for known duplicate noise
        errors: list[str] = []
        for path, docs in pending_by_file.items():
            for d in docs:
                dt = d.get("doctype")
                nm = d.get("name") or d.get("_match") or "<unknown>"
                errors.append(f"  - {path}: {dt} / {nm}")

        msg = (
            "[reload_all_doctypes] Could not apply some document(s) after all passes.\n"
            "These are REAL errors (the doctype was not loaded/updated):\n" + "\n".join(errors)
        )
        # Log and raise a concise exception so CI/bench gets a non-zero exit
        frappe.logger().error(msg)
        raise RuntimeError(msg)

    frappe.logger().info(
        f"[reload_all_doctypes] Finished. Applied {total_applied} change(s) in up to {max_passes} passes from {base_dir}."
    )
