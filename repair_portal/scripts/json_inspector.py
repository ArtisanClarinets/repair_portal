#!/usr/bin/env python3
"""
json_inspector.py  –  Locate and sanity-check every *.json file under the
repair_portal app and report anything that could raise:
    TypeError: 'str' object does not support item assignment
"""

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

APP_ROOT = pathlib.Path(__file__).resolve().parents[1]  # points to .../repair_portal
TARGET_EXT = ".json"


def walk_json_files(root: pathlib.Path):
    """Yield every *.json file under *root*."""
    for p in root.rglob(f"*{TARGET_EXT}"):
        if p.is_file():
            yield p


def poke(node: Any) -> None:
    """
    Try the same assignment Frappe makes on mappings.
    If *node* isn't dict-like (e.g. it's a str), Python will raise TypeError.
    """
    # Don't really mutate the structure – do it on a shallow copy
    try:
        tmp = node.copy() if isinstance(node, dict) else node  # type: ignore
        tmp["__probe__"] = None  # type: ignore
    except Exception as exc:
        raise exc  # propagate so caller can turn it into a report


def traverse(
    node: Any,
    abs_path: pathlib.Path,
    stack: list[str],
    faults: list[tuple[pathlib.Path, str]],
) -> None:
    """Depth-first walk; record path + message for every suspect node."""
    if isinstance(node, dict):
        for k, v in node.items():
            traverse(v, abs_path, stack + [str(k)], faults)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            traverse(item, abs_path, stack + [f"[{idx}]"], faults)
    else:
        try:
            poke(node)
        except TypeError as te:
            faults.append((abs_path, f'{".".join(stack) or "<root>"} → {te}'))


def main() -> None:
    root = APP_ROOT
    if not root.exists():
        sys.exit(f"✘ App root {root} does not exist")

    offenders: list[tuple[pathlib.Path, str]] = []

    for json_file in walk_json_files(root):
        try:
            with json_file.open(encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            offenders.append((json_file.resolve(), f"Cannot load JSON → {e}"))
            continue

        traverse(data, json_file.resolve(), [], offenders)

    if offenders:
        print("⚠️  Potentially problematic JSON files:")
        for fp, msg in offenders:
            print(f"  • {fp}: {msg}")
        sys.exit(1)
    else:
        print("✓ No structural issues detected that match the reported TypeError.")


if __name__ == "__main__":
    main()
