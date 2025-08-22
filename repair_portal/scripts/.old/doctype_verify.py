#!/usr/bin/env python3
# /opt/frappe/erp-bench/apps/repair_portal/repair_portal/scripts/doctype_verify.py
# Date: 2025-06-16
# Version: 1.3
# Purpose: Validate Frappe V15 DocType JSON files for required fields & values,
#          including specific checks for 'istable' DocTypes.
#
# Usage examples:
#   python doctype_verify.py --app erpnext --app repair_portal
#   python doctype_verify.py /full/path/to/any/folder
#
#
# Exit-code: 0 → all good · 1 → validation errors · 2 → CLI/IO problems
# -----------------------------------------------------------------------------

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURATION – tweak as needed
# ---------------------------------------------------------------------------

REQUIRED_CONFIGS: dict[str, dict[str, object]] = {
    'DocType': {
        'required_fields': ['doctype', 'name', 'module', 'fields', 'permissions'],
        'mandatory_values': {'doctype': 'DocType'},
        'istable_required_fields': ['parent', 'parenttype', 'parentfield', 'idx'],
    },
    'Report': {
        'required_fields': [
            'doctype',
            'name',
            'report_name',
            'ref_doctype',
            'report_type',
            'is_standard',
        ],
        'mandatory_values': {'doctype': 'Report', 'is_standard': 'Yes'},
    },
    'Workflow': {
        'required_fields': [
            'doctype',
            'name',
            'workflow_name',
            'document_type',
            'states',
            'transitions',
        ],
        'mandatory_values': {'doctype': 'Workflow'},
    },
    'Workspace': {
        'required_fields': ['doctype', 'name', 'label', 'module', 'links'],
        'mandatory_values': {'doctype': 'Workspace'},
    },
    'Dashboard Chart': {
        'required_fields': [
            'doctype',
            'name',
            'chart_name',
            'chart_type',
            'document_type',
        ],
        'mandatory_values': {'doctype': 'Dashboard Chart'},
    },
    'Dashboard': {
        'required_fields': ['doctype', 'name', 'dashboard_name', 'charts', 'cards'],
        'mandatory_values': {'doctype': 'Dashboard'},
    },
    'Web Form': {
        'required_fields': ['doctype', 'title', 'doc_type', 'web_form_fields'],
        'mandatory_values': {'doctype': 'Web Form'},
    },
    'Notification': {
        'required_fields': [
            'doctype',
            'name',
            'channel',
            'document_type',
            'send_on',
            'message',
        ],
        'mandatory_values': {'doctype': 'Notification'},
    },
    'Client Script': {
        'required_fields': ['doctype', 'dt', 'script_type', 'script'],
        'mandatory_values': {'doctype': 'Client Script'},
    },
    'Print Format': {
        'required_fields': ['doctype', 'doc_type', 'print_format_type', 'standard'],
        'mandatory_values': {'doctype': 'Print Format', 'standard': 1},
    },
    'Page': {
        'required_fields': ['doctype', 'name', 'title', 'module'],
        'mandatory_values': {'doctype': 'Page'},
    },
}

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------


def get_doc_type_from_data(data: dict) -> str | None:
    """Return the DocType name if present, else None."""
    return data.get('doctype')


def validate_json_file(file_path: Path) -> list[str]:
    """Validate one JSON file and return a list of error strings (empty if OK)."""
    errors: list[str] = []

    try:
        with file_path.open('r', encoding='utf-8') as fh:
            data = json.load(fh)
    except json.JSONDecodeError:
        errors.append(f'🚫 Invalid JSON format in: {file_path}')
        return errors
    except Exception as exc:
        errors.append(f'⚠️  Error reading {file_path}: {exc}')
        return errors

    doc_type = get_doc_type_from_data(data)
    if not doc_type or doc_type not in REQUIRED_CONFIGS:
        # Unknown or irrelevant JSON – silently ignore.
        return []

    cfg = REQUIRED_CONFIGS[doc_type]
    required_fields: list[str] = cfg.get('required_fields', [])  # type: ignore
    mandatory_values: dict[str, str] = cfg.get('mandatory_values', {})  # type: ignore
    istable_required_fields: list[str] = cfg.get('istable_required_fields', [])  # type: ignore

    # 1️⃣ Missing fields
    missing = [fld for fld in required_fields if fld not in data]
    if missing:
        errors.append(f'❌ {file_path}: Missing required field(s) for "{doc_type}": {missing}')

    # 2️⃣ Mandatory values (case-insensitive for strings)
    for fld, expected in mandatory_values.items():
        if fld in data:
            actual = data[fld]
            if str(actual).lower() != str(expected).lower():
                errors.append(
                    f"❌ {file_path}: Invalid value for '{fld}'. "
                    f'Expected "{expected}", found "{actual}".'
                )

    # 3️⃣ istable specific checks
    if doc_type == 'DocType' and data.get('istable') == 1:
        doc_type_fields = {field.get('fieldname') for field in data.get('fields', [])}
        missing_istable_fields = [
            fld for fld in istable_required_fields if fld not in doc_type_fields
        ]
        if missing_istable_fields:
            errors.append(
                f'❌ {file_path}: DocType is istable: 1 but missing required table field(s): {missing_istable_fields}'
            )

    return errors


def scan_all_jsons(app_root: Path) -> int:
    """Walk an app folder, validate every .json, and print a report."""
    all_errors: list[str] = []
    json_count = 0

    for dirpath, _dirs, filenames in os.walk(app_root):
        for fname in filenames:
            if fname.endswith('.json'):
                json_count += 1
                errs = validate_json_file(Path(dirpath) / fname)
                all_errors.extend(errs)

    if json_count == 0:
        logging.warning('⚠️  No JSON files found under: %s', app_root)
        return 1

    if all_errors:
        print('\n--- Validation Errors Found ---\n')
        print('\n'.join(all_errors))
        print(
            f'\n❌ Validation failed: {len(all_errors)} error(s) across {json_count} JSON file(s).'
        )
        return 1

    print(f"✅ All {json_count} JSON file(s) in '{app_root}' are compliant.")
    return 0


def find_bench_root(start: Path) -> Path | None:
    """Climb parents until a folder containing both 'apps' & 'sites' appears."""
    for parent in [start, *start.parents]:
        if (parent / 'apps').is_dir() and (parent / 'sites').is_dir():
            return parent
    return None


# ---------------------------------------------------------------------------
# COMMAND-LINE INTERFACE
# ---------------------------------------------------------------------------


def cli() -> int:  # → exit code
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    parser = argparse.ArgumentParser(description='Validate Frappe DocType JSON files (v1.3)')
    parser.add_argument(
        'path',
        nargs='?',
        metavar='PATH',
        help='Explicit folder to scan (skip --app flags)',
    )
    parser.add_argument(
        '-a',
        '--app',
        dest='apps',
        action='append',
        metavar='APPNAME',
        help='App(s) inside the current bench to scan. Use multiple --app flags for multiple apps.',
    )

    args = parser.parse_args()

    # 1️⃣ Explicit path wins
    if args.path:
        target = Path(args.path).resolve()
        if not target.is_dir():
            parser.error(f"Provided path '{target}' is not a directory")
        return scan_all_jsons(target)

    # 2️⃣ Otherwise we need at least one --app
    if not args.apps:
        parser.error('Specify a PATH or at least one --app flag')

    bench_root = find_bench_root(Path.cwd())
    if not bench_root:
        parser.error("Could not locate bench root (looked for 'apps' & 'sites')")

    exit_code = 0
    for app in args.apps:
        app_path = bench_root / 'apps' / app / app
        if not app_path.is_dir():
            logging.error("⚠️  Skipping unknown app '%s' (no folder %s)", app, app_path)
            exit_code = 1
            continue

        res = scan_all_jsons(app_path)
        exit_code = exit_code or res  # propagate any failure

    return exit_code


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit(cli())
# ---------------------------------------------------------------------------
# End of file
# --------------------------------------------------------------------------
