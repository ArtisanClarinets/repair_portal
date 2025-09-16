# -*- coding: utf-8 -*-
"""
Validates transition references, orphan states, missing masters.
Run: bench execute repair_portal.utils.workflows.validate:run
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import frappe

APP_ROOT = Path("/home/frappe/frappe-bench/apps/repair_portal")
CODE_ROOT = APP_ROOT / "repair_portal"

def _load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def run() -> Dict[str, Any]:
    issues = {
        "missing_action_master": [],
        "missing_state_master": [],
        "missing_next_state": [],
        "missing_from_state": [],
        "orphans_nonterminal": []
    }
    action_masters = set(x.name for x in frappe.get_all("Workflow Action Master", fields=["name"]))
    state_masters = set(x.name for x in frappe.get_all("Workflow State", fields=["name"]))

    for p in CODE_ROOT.rglob("*.json"):
        data = _load_json(p)
        if not data:
            continue
        items = data if isinstance(data, list) else [data]
        for d in items:
            if not isinstance(d, dict) or d.get("doctype") != "Workflow":
                continue
            name = d.get("name")
            sts = [s.get("state") for s in d.get("states") or [] if s.get("state")]
            sts_set = set(sts)

            # missing masters
            for t in d.get("transitions") or []:
                a = t.get("action")
                if a and a not in action_masters:
                    issues["missing_action_master"].append((name, a))
            for s in sts:
                if s not in state_masters:
                    issues["missing_state_master"].append((name, s))

            # missing refs
            for t in d.get("transitions") or []:
                if t.get("state") not in sts_set:
                    issues["missing_from_state"].append((name, t))
                if t.get("next_state") not in sts_set:
                    issues["missing_next_state"].append((name, t))

            # orphans (no outgoing) except docstatus==2
            out_map = {s:0 for s in sts}
            for t in d.get("transitions") or []:
                if t.get("state") in out_map:
                    out_map[t.get("state")] += 1
            ds_map = {s.get("state"): s.get("doc_status") for s in d.get("states") or []}
            orphans = [s for s, cnt in out_map.items() if cnt == 0 and ds_map.get(s) != 2]
            if orphans:
                issues["orphans_nonterminal"].append((name, orphans))

    frappe.msgprint(f"Workflow validation report:\n{json.dumps(issues, indent=2)}")
    return issues
