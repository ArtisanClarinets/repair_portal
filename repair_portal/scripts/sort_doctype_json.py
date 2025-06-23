# /opt/frappe/erp-bench/apps/repair_portal/repair_portal/scripts/sort_doctype_json.py
# Date Updated: 2025-07-02
# Version: 1.0
# Purpose: Sort keys within DocType JSON files for stable diffs.
# Dev notes: sorts nested lists by common fields like fieldname and role.

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

DEFAULT_SORT_ORDER = [
    "doctype",
    "name",
    "owner",
    "modified",
    "module",
    "custom",
    "fields",
    "permissions",
    "links",
    "actions",
    "doctype_version",
]


def sort_dict(d: dict[str, Any]) -> dict[str, Any]:
    ordered: dict[str, Any] = {}
    for key in DEFAULT_SORT_ORDER:
        if key in d:
            ordered[key] = d[key]
    for key in sorted(k for k in d if k not in DEFAULT_SORT_ORDER):
        ordered[key] = d[key]
    return ordered


def sort_lists(data: dict[str, Any]) -> None:
    if "fields" in data and isinstance(data["fields"], list):
        data["fields"].sort(key=lambda f: f.get("fieldname", ""))
    if "permissions" in data and isinstance(data["permissions"], list):
        data["permissions"].sort(key=lambda p: (p.get("permlevel", 0), p.get("role", "")))
    if "links" in data and isinstance(data["links"], list):
        data["links"].sort(key=lambda link: link.get("link_doctype", ""))

    for field in data.get("fields", []):
        if isinstance(field, dict) and "options" in field and isinstance(field["options"], list):
            field["options"].sort()


def load_json(path: pathlib.Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: pathlib.Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def process_file(path: pathlib.Path) -> None:
    data = load_json(path)
    if isinstance(data, dict):
        sort_lists(data)
        data = sort_dict(data)
    write_json(path, data)
    print(f"✓ Sorted {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sort DocType JSON files")
    parser.add_argument("files", nargs="+", help="Path(s) to DocType JSON files")
    args = parser.parse_args()

    for file_path in args.files:
        fp = pathlib.Path(file_path)
        if not fp.exists():
            print(f"✘ {fp} does not exist")
            continue
        try:
            process_file(fp)
        except Exception as e:  # noqa: BLE001
            print(f"✘ Failed to sort {fp}: {e}")


if __name__ == "__main__":
    main()
