"""
Workflow standardizer for Frappe v15.
Run with: bench execute repair_portal.utils.workflows.standardize:apply --kwargs '{}'
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import frappe

APP_ROOT = Path("/home/frappe/frappe-bench/apps/repair_portal")
CODE_ROOT = APP_ROOT / "repair_portal"

# Roles to allow editing in Draft states when empty (safe defaults)
DEFAULT_EDIT_ROLES = ["System Manager"]


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _dump_json(path: Path, data: Any):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _iter_workflow_docs() -> list[tuple[Path, dict[str, Any]]]:
    res = []
    for p in CODE_ROOT.rglob("*.json"):
        data = _load_json(p)
        if not data:
            continue
        items = data if isinstance(data, list) else [data]
        for d in items:
            if isinstance(d, dict) and d.get("doctype") == "Workflow":
                res.append((p, d))
    return res


def _iter_doctype_docs() -> dict[str, dict[str, Any]]:
    out = {}
    for p in CODE_ROOT.rglob("*.json"):
        data = _load_json(p)
        if not data:
            continue
        items = data if isinstance(data, list) else [data]
        for d in items:
            if isinstance(d, dict) and d.get("doctype") == "DocType":
                out[d.get("name")] = d
    return out


def _ensure_custom_field(dt: str):
    """Ensure 'workflow_state' field exists (Link → Workflow State)."""
    if frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "workflow_state"}):
        return
    cf = frappe.get_doc(
        {
            "doctype": "Custom Field",
            "dt": dt,
            "fieldname": "workflow_state",
            "label": "Workflow State",
            "fieldtype": "Link",
            "options": "Workflow State",
            "read_only": 1,
            "in_list_view": 1,
        }
    )
    cf.insert(ignore_permissions=True)


def dry_run() -> dict[str, Any]:
    """Report only—no changes."""
    wfs = _iter_workflow_docs()
    doctypes = _iter_doctype_docs()
    missing_field = []
    wrong_field = []
    str_docstatus = []
    empty_edit = []

    for p, wf in wfs:
        dt = wf.get("document_type")
        ws_field = wf.get("workflow_state_field")
        if ws_field != "workflow_state":
            wrong_field.append((wf.get("name"), dt, ws_field))
        # check target doctype has the field (via schema or custom field)
        has_field = False
        if dt in doctypes:
            fields = doctypes[dt].get("fields") or []
            has_field = any(f.get("fieldname") == "workflow_state" for f in fields)
        # also check DB Custom Field
        if not has_field and not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": "workflow_state"}):
            missing_field.append((wf.get("name"), dt))

        # states/docstatus checks
        for s in wf.get("states") or []:
            ds = s.get("doc_status")
            if isinstance(ds, str):
                str_docstatus.append((wf.get("name"), s.get("state"), ds))
            allow = s.get("allow_edit") or []
            if not allow and (s.get("doc_status") in (0, "0")):
                empty_edit.append((wf.get("name"), s.get("state")))

    return {
        "workflows": len(wfs),
        "wrong_workflow_state_field": wrong_field,
        "missing_workflow_state_field": missing_field,
        "string_docstatus": str_docstatus,
        "empty_allow_edit_on_draft": empty_edit,
    }


def apply(fix_allow_edit: bool = True) -> dict[str, Any]:
    """Apply standardization:
    - Set workflow_state_field='workflow_state'
    - Ensure Custom Field exists on each target Doctype
    - Convert string doc_status -> int (0/1/2)
    - Optionally add DEFAULT_EDIT_ROLES to Draft states with empty allow_edit
    """
    report = {"updated_files": [], "created_custom_fields": [], "normalized_states": 0, "edit_roles_added": 0}

    # 1) ensure CF on doctypes used
    wfs = _iter_workflow_docs()
    used_dts = sorted({wf.get("document_type") for _, wf in wfs if wf.get("document_type")})
    for dt in used_dts:
        _ensure_custom_field(dt)
        report["created_custom_fields"].append(dt)

    # 2) update workflow JSONs in-place
    for p, wf in wfs:
        changed = False

        # field name
        if wf.get("workflow_state_field") != "workflow_state":
            wf["workflow_state_field"] = "workflow_state"
            changed = True

        # state docstatus ints + allow_edit defaults
        for s in wf.get("states") or []:
            ds = s.get("doc_status")
            if isinstance(ds, str) and ds in ("0", "1", "2"):
                s["doc_status"] = int(ds)
                changed = True
            if fix_allow_edit and s.get("doc_status") == 0 and not (s.get("allow_edit") or []):
                s["allow_edit"] = [{"role": r} for r in DEFAULT_EDIT_ROLES]
                report["edit_roles_added"] += 1
                changed = True
            if isinstance(s.get("doc_status"), bool):  # guard against True/False by mistake
                s["doc_status"] = 1 if s["doc_status"] else 0
                changed = True

        if changed:
            # Write back to the JSON file
            data = _load_json(p)
            items = data if isinstance(data, list) else [data]
            for idx, d in enumerate(items):
                if isinstance(d, dict) and d.get("doctype") == "Workflow" and d.get("name") == wf.get("name"):
                    items[idx] = wf
            _dump_json(p, items if isinstance(data, list) else items[0])
            report["updated_files"].append(str(p))

    return report
