#!/usr/bin/env python3
"""Generate a permissions matrix for DocTypes in repair_portal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

APP_ROOT = Path(__file__).resolve().parents[1]
OPS_ROOT = APP_ROOT / "OPS"


def load_doctype_permissions() -> Dict[str, List[dict]]:
    mapping: Dict[str, List[dict]] = {}
    for json_path in APP_ROOT.glob("**/doctype/*/*.json"):
        try:
            data = json.loads(json_path.read_text())
        except json.JSONDecodeError:
            continue
        if data.get("doctype") != "DocType":
            continue
        permissions = data.get("permissions") or []
        mapping[data["name"]] = permissions
    return mapping


def build_markdown(matrix: Dict[str, List[dict]]) -> str:
    lines = ["# Security Permissions Matrix", "", "DocType | Role | Create | Read | Write | Delete | Submit | Cancel | Amend | If Owner", "--- | --- | --- | --- | --- | --- | --- | --- | --- | ---"]
    for doctype, permissions in sorted(matrix.items()):
        for perm in permissions:
            lines.append(
                " | ".join(
                    [
                        doctype,
                        perm.get("role", "-"),
                        "✅" if perm.get("create") else "-",
                        "✅" if perm.get("read") else "-",
                        "✅" if perm.get("write") else "-",
                        "✅" if perm.get("delete") else "-",
                        "✅" if perm.get("submit") else "-",
                        "✅" if perm.get("cancel") else "-",
                        "✅" if perm.get("amend") else "-",
                        "✅" if perm.get("if_owner") else "-",
                    ]
                )
            )
        if not permissions:
            lines.append(f"{doctype} | (no roles) | - | - | - | - | - | - | - | -")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    OPS_ROOT.mkdir(exist_ok=True)
    matrix = load_doctype_permissions()
    (OPS_ROOT / "SECURITY_PERMISSIONS_MATRIX.md").write_text(build_markdown(matrix))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
