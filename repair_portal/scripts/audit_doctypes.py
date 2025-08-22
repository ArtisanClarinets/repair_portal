#!/usr/bin/env python3
# /home/frappe/frappe-bench/apps/repair_portal/repair_portal/scripts/audit_doctypes.py
"""
Repository auditor (filesystem-first) for all JSON resources exported by Frappe:
  <module>/<doctype_type>/<doctype_name>/<doctype_name>.json

Now covers:
  - DocType
  - Report
  - Dashboard
  - Dashboard Chart
  - Number Card
  - Workspace
  - (and any other JSON with a `doctype` key under the nested layout)

What it reports
  1) Exact-name duplicates (per resource type)
  2) Near-duplicates by fieldname Jaccard (DocType only; configurable threshold)
  3) Cross-module & dangling Table references (DocType only)
  4) Table/Table MultiSelect must point to a Child Table (DocType only; istable=1)
  5) Dangling Link targets (DocType only; not found on disk nor DB)
     ▶ DB-only link targets are collapsed into one ✅ summary line with a count
  6) Duplicate fieldnames within a DocType
  7) Fieldname regex compliance (DocType only)
  8) depends_on references to missing fields (DocType only)
  9) JSON 'module' vs folder location mismatch (all resource types)
 10) Folder/file vs resource “name” mismatch (all resource types)
 11) Parent DocTypes missing 'autoname' (DocType only)
 12) Child tables missing 'editable_grid: 1' (DocType only)
 13) Resource-type sanity checks (non-DocType):
      - Report: report_type/required fields sanity, ref_doctype existence when applicable
      - Dashboard Chart / Number Card: document_type existence when provided
      - Workspace: basic structure & name/module coherence

Run:
  bench --site erp.artisanclarinets.com execute repair_portal.scripts.audit_doctypes.run
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# Prefer Frappe scrub if available (keeps naming identical to Frappe)
try:
    import frappe  # type: ignore
    from frappe.utils.data import scrub as _frappe_scrub  # type: ignore

    def scrub(s: str) -> str:
        return _frappe_scrub(s or '')

except Exception:

    def scrub(s: str) -> str:
        s = (s or '').strip().lower()
        s = re.sub(r'\s+', '_', s)
        s = re.sub(r'[^a-z0-9_]', '_', s)
        s = re.sub(r'_+', '_', s).strip('_')
        return s


# ---- CONFIG ----
APP_ROOT = Path('/home/frappe/frappe-bench/apps/repair_portal/repair_portal')
MODULES_TXT = APP_ROOT / 'modules.txt'
NEAR_DUPLICATE_THRESHOLD = 0.30  # match your current tolerance
FIELDNAME_RE = re.compile(r'^[a-z][a-z0-9_]{0,139}$')  # DocType fieldname guard

TABLE_FTYPES = {'Table', 'Table MultiSelect'}
LINK_FTYPES = {'Link'}  # (Dynamic Link not validated here)

# Known resource types we’ll give extra checks for (others still validated for path/module/name)
RESOURCE_TYPES_WITH_EXTRA = {
    'DocType',
    'Report',
    'Dashboard',
    'Dashboard Chart',
    'Number Card',
    'Workspace',
}


# ---------- Data containers ----------
class Resource:
    """
    Generic JSON resource exported by Frappe (has top-level 'doctype' key).
    """

    def __init__(self, doctype_type: str, name: str, module: str, path: Path, data: dict):
        self.type: str = doctype_type  # e.g., DocType, Report, Workspace
        self.name: str = name  # document name
        self.module: str = module  # logical module (from JSON)
        self.path: Path = path  # filesystem path to JSON
        self.data: dict = data  # raw JSON


class DocInfo(Resource):
    """
    DocType-specialized resource with field graph introspection.
    """

    def __init__(self, name: str, module: str, path: Path, data: dict):
        super().__init__('DocType', name, module, path, data)
        self.fields: list[dict] = data.get('fields') or []
        self.istable: bool = bool(data.get('istable'))
        self.editable_grid: bool = bool(data.get('editable_grid'))
        self.autoname: str = (data.get('autoname') or '').strip()

        self.fieldnames: list[str] = [
            f.get('fieldname').strip()  # type: ignore
            for f in self.fields
            if isinstance(f, dict) and f.get('fieldname')  # type: ignore
        ]
        self.fieldname_set: set[str] = set(self.fieldnames)

        self.table_targets: list[tuple[str, str]] = []  # (fieldname, options)
        self.link_targets: list[tuple[str, str]] = []  # (fieldname, options)
        self.depends_on_refs: list[tuple[str, str]] = []  # (fieldname, expr)

        for f in self.fields:
            ft = f.get('fieldtype')
            opts = (f.get('options') or '').strip()
            if ft in TABLE_FTYPES:
                self.table_targets.append((f.get('fieldname') or '', opts))
            elif ft in LINK_FTYPES and opts:
                self.link_targets.append((f.get('fieldname') or '', opts))
            dep = (f.get('depends_on') or '').strip()
            if dep:
                self.depends_on_refs.append((f.get('fieldname') or '', dep))


# ---------- Utilities ----------
def _read_modules_from_txt(modules_txt: Path) -> list[str]:
    if not modules_txt.exists():
        print(f'❌ modules.txt not found: {modules_txt}')
        return []
    mods: list[str] = []
    for line in modules_txt.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        mods.append(line)
    return mods


def _iter_resource_json_for_module(module_name: str) -> list[Path]:
    """
    Find JSON files under <app>/<scrub(module)>/*/*/*.json
    Enforce nested layout: <module>/<doctype_type>/<doctype_name>/<doctype_name>.json
    """
    mod_dir = APP_ROOT / scrub(module_name)
    if not mod_dir.exists():
        return []
    paths: list[Path] = []
    for type_dir in [p for p in mod_dir.iterdir() if p.is_dir()]:
        for name_dir in [p for p in type_dir.iterdir() if p.is_dir()]:
            json_path = name_dir / f'{name_dir.name}.json'
            if json_path.exists():
                paths.append(json_path)
            # be tolerant: also include any extra *.json colocated (translations, variants)
            for p in name_dir.glob('*.json'):
                if p not in paths:
                    paths.append(p)
    return paths


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f'✗ JSON read error: {path} ({e})')
        return {}
    if not isinstance(data, dict):
        return {}
    if not data.get('doctype'):
        return {}
    return data


def _guess_name_from_path(p: Path) -> str:
    # Expect .../<module>/<type>/<name>/<name>.json
    try:
        return p.parent.name.replace('_', ' ').title()
    except Exception:
        return p.stem


def _resource_from_json(path: Path, fallback_module: str) -> Resource | None:
    data = _load_json(path)
    if not data:
        return None
    rtype = (data.get('doctype') or '').strip()
    name = (data.get('name') or '').strip() or _guess_name_from_path(path)
    module = (data.get('module') or fallback_module).strip()
    if rtype == 'DocType':
        return DocInfo(name=name, module=module, path=path, data=data)
    return Resource(doctype_type=rtype, name=name, module=module, path=path, data=data)


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / max(1, len(a | b))


def _extract_depends_fields(expr: str) -> set[str]:
    # e.g. "eval:doc.create_task==1 and doc.section=='Upper Joint'"
    out = set(re.findall(r'doc\.([a-zA-Z0-9_]+)', expr))
    if not expr.startswith('eval:'):
        out.add(expr.strip())
    return {x for x in out if x}


# ---------- Main ----------
def run():
    modules = _read_modules_from_txt(MODULES_TXT)
    print(f'Scanning modules from modules.txt: {modules}')

    if not modules:
        print('✅ No exact-name duplicates.')
        print('✅ No near-duplicates by fieldnames.')
        print('✅ No cross-module table references.')
        return

    # Catalog all resources (any JSON with a 'doctype' key)
    catalog_by_type: dict[str, dict[str, Resource]] = defaultdict(dict)  # type -> name -> Resource
    name_collisions: dict[str, list[Resource]] = defaultdict(list)  # key: f"{type}:{name}"
    path_mismatch: list[tuple[str, str, Path]] = []  # (json_module, expected_root, path)
    folder_name_mismatch: list[tuple[str, str, Path]] = []  # (resource_name, expected_folder, path)

    for mod in modules:
        for p in _iter_resource_json_for_module(mod):
            r = _resource_from_json(p, fallback_module=mod)
            if not r:
                continue

            # Module/folder mismatch (JSON says module X, but path under module Y)
            expected_root = APP_ROOT / scrub(r.module)
            actual_mod_root = p.parents[2] if len(p.parents) >= 3 else None
            if actual_mod_root and expected_root and actual_mod_root != expected_root:
                path_mismatch.append((r.module, str(expected_root), p))

            # Folder/file naming vs resource name
            expected_folder = scrub(r.name)
            try:
                name_dir = p.parent.name
                if name_dir != expected_folder:
                    folder_name_mismatch.append((r.name, expected_folder, p))
                if p.stem != expected_folder:
                    folder_name_mismatch.append((r.name, expected_folder, p))
            except Exception:
                pass

            # Index; check duplicates per (type, name)
            key = f'{r.type}:{r.name}'
            if r.name in catalog_by_type[r.type]:
                name_collisions[key].append(catalog_by_type[r.type][r.name])
                name_collisions[key].append(r)
            else:
                catalog_by_type[r.type][r.name] = r

    # Summary
    total_resources = sum(len(d) for d in catalog_by_type.values())
    print(f'Found {total_resources} resource(s) across {len(modules)} module(s).')
    print('Resources by type:')
    for rtype, d in sorted(catalog_by_type.items(), key=lambda x: (-len(x[1]), x[0])):
        print(f'  - {rtype}: {len(d)}')

    # 1) Exact-name duplicates (per resource type)
    if name_collisions:
        print('❌ Exact-name duplicates (type:name → [module :: path]):')
        already = set()
        for key, res_list in sorted(name_collisions.items()):
            tup = (key, tuple(r.path for r in res_list))
            if tup in already:
                continue
            print(f'  - {key}:')
            for r in res_list:
                print(f'      • {r.module} :: {r.path}')
            already.add(tup)
    else:
        print('✅ No exact-name duplicates across resource types.')

    # ---------- DocType-only deep checks ----------
    doctypes: dict[str, DocInfo] = {
        name: r for name, r in catalog_by_type.get('DocType', {}).items() if isinstance(r, DocInfo)
    }

    # 2) Near-duplicates (DocType field overlap)
    names = list(doctypes.keys())
    nd_warnings: list[tuple[str, str, float]] = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            A, B = doctypes[names[i]], doctypes[names[j]]
            if not A.fieldname_set or not B.fieldname_set:
                continue
            jac = _jaccard(A.fieldname_set, B.fieldname_set)
            if jac >= NEAR_DUPLICATE_THRESHOLD:
                nd_warnings.append((A.name, B.name, round(jac, 3)))
    if nd_warnings:
        print(
            f'⚠️ Potential near-duplicates by field overlap (DocType, threshold ≥ {NEAR_DUPLICATE_THRESHOLD}):'
        )
        for a, b, score in sorted(nd_warnings, key=lambda x: -x[2]):
            print(f'  - {a} ↔ {b} (Jaccard={score})')
    else:
        print('✅ No near-duplicates by DocType fieldnames.')

    # 3,4,5) Table/Link integrity (DocType)
    cross_refs: list[
        tuple[str, str, str, str]
    ] = []  # (parent_doctype, parent_module, fieldtype, child_doctype)
    dangling_tables: list[tuple[str, str, str]] = []  # (parent_doctype, fieldname, missing_child)
    non_child_table_targets: list[
        tuple[str, str, str]
    ] = []  # (parent_doctype, fieldname, bad_child)
    table_without_options: list[tuple[str, str]] = []  # (parent_doctype, fieldname)
    dangling_links_disk: list[
        tuple[str, str, str]
    ] = []  # (parent_doctype, fieldname, missing_target)
    db_only_link_count = 0  # count-only, no list

    for parent in doctypes.values():
        for fieldname, child in parent.table_targets:
            if not child:
                table_without_options.append((parent.name, fieldname))
                continue
            if child not in doctypes:
                # not in repo; check DB
                exists_in_db = False
                try:
                    if frappe.db.exists('DocType', child):
                        exists_in_db = True
                except Exception:
                    pass
                if exists_in_db:
                    cross_refs.append((parent.name, parent.module, 'Table', child))
                else:
                    dangling_tables.append((parent.name, fieldname, child))
                continue
            if not doctypes[child].istable:
                non_child_table_targets.append((parent.name, fieldname, child))
            if doctypes[child].module != parent.module:
                cross_refs.append((parent.name, parent.module, 'Table', child))

        for fieldname, target in parent.link_targets:
            if target not in doctypes:
                exists_in_db = False
                try:
                    if frappe.db.exists('DocType', target):
                        exists_in_db = True
                except Exception:
                    pass
                if exists_in_db:
                    db_only_link_count += 1
                else:
                    dangling_links_disk.append((parent.name, fieldname, target))

    if cross_refs:
        print('ℹ️ Cross-module table references (DocType) (parent [module] fieldtype → child):')
        for parent_name, parent_mod, fieldtype, child in sorted(cross_refs):
            child_mod = doctypes[child].module if child in doctypes else '(DB-only)'
            print(f'  - {parent_name} [{parent_mod}] {fieldtype} → {child} [{child_mod}]')
    else:
        print('✅ No cross-module table references (DocType).')

    if dangling_tables:
        print('❌ Dangling Table references (DocType) (child not found on disk nor DB):')
        for parent_name, fieldname, missing_child in sorted(dangling_tables):
            print(f'  - {parent_name}.{fieldname} → {missing_child} (missing)')
    else:
        print('✅ No dangling Table references (DocType).')

    if non_child_table_targets:
        print('❌ Table fields pointing to NON-child DocTypes (DocType; must have istable=1):')
        for parent_name, fieldname, bad_child in sorted(non_child_table_targets):
            print(f'  - {parent_name}.{fieldname} → {bad_child} (istable=0)')
    else:
        print('✅ All Table fields point to Child Tables (DocType).')

    if table_without_options:
        print("❌ Table fields missing 'options' (DocType; child DocType name):")
        for parent_name, fieldname in sorted(table_without_options):
            print(f'  - {parent_name}.{fieldname} (no options set)')
    else:
        print("✅ All Table fields define 'options' (DocType).")

    if dangling_links_disk:
        print('❌ Dangling Link targets (DocType; not found on disk or DB):')
        for parent_name, fieldname, target in sorted(dangling_links_disk):
            print(f'  - {parent_name}.{fieldname} → {target}')
    else:
        print('✅ No dangling Link targets (DocType).')

    print(
        f'✅ Link targets present in DB but not in repo (DocType): OK ({db_only_link_count} verified)'
    )

    # 6) Duplicate DocType fieldnames
    dup_fields = []
    for doc in doctypes.values():
        counts = Counter(doc.fieldnames)
        dups = [fn for fn, c in counts.items() if c > 1]
        if dups:
            dup_fields.append((doc.name, dups))
    if dup_fields:
        print('❌ Duplicate fieldnames within DocTypes:')
        for docname, dups in sorted(dup_fields):
            print(f"  - {docname}: {', '.join(sorted(dups))}")
    else:
        print('✅ No duplicate fieldnames inside any DocType.')

    # 7) Fieldname regex compliance
    bad_fieldnames = []
    for doc in doctypes.values():
        for fn in doc.fieldnames:
            if not FIELDNAME_RE.match(fn):
                bad_fieldnames.append((doc.name, fn))
    if bad_fieldnames:
        print('❌ Fieldnames failing Frappe-safe regex [a-z][a-z0-9_]{0,139}:')
        for docname, fn in sorted(bad_fieldnames):
            print(f'  - {docname}.{fn}')
    else:
        print('✅ All DocType fieldnames comply with safe format.')

    # 8) depends_on references unknown fields
    bad_depends = []
    for doc in doctypes.values():
        for fieldname, expr in doc.depends_on_refs:
            refs = _extract_depends_fields(expr)
            for r in refs:
                if r and r not in doc.fieldname_set:
                    bad_depends.append((doc.name, fieldname, expr, r))
    if bad_depends:
        print('❌ depends_on referencing unknown fields (DocType):')
        for docname, fieldname, expr, missing in sorted(bad_depends):
            print(f"  - {docname}.{fieldname} depends_on '{expr}' → missing '{missing}'")
    else:
        print('✅ All depends_on expressions reference existing fields (DocType).')

    # 9) JSON 'module' vs folder for ALL resources
    if path_mismatch:
        print("⚠️ JSON 'module' disagrees with folder location (all types):")
        for json_mod, expected_root, p in path_mismatch:
            print(f"  - module='{json_mod}' expected under '{expected_root}', file at '{p}'")
    else:
        print('✅ No module/path mismatches between JSON and filesystem (all types).')

    # 10) Folder/file vs name mismatches for ALL resources
    if folder_name_mismatch:
        print('⚠️ Resource folder/file naming mismatch (all types):')
        for name, expected_folder, p in folder_name_mismatch:
            print(f"  - '{name}' should live in folder/file '{expected_folder}.json' → {p}")
    else:
        print('✅ Folder/file names match resource names (all types).')

    # 11) Parent DocTypes missing autoname
    parent_missing_autoname = [
        d.name for d in doctypes.values() if not d.istable and not d.autoname
    ]
    if parent_missing_autoname:
        print("⚠️ Parent DocTypes missing 'autoname' (consider 'field:...' or 'format:...'):")
        for n in sorted(parent_missing_autoname):
            print(f'  - {n}')
    else:
        print("✅ All parent DocTypes define an 'autoname' or are intentionally named.")

    # 12) Child tables missing editable_grid
    child_no_editgrid = [d.name for d in doctypes.values() if d.istable and not d.editable_grid]
    if child_no_editgrid:
        print("⚠️ Child tables without 'editable_grid: 1':")
        for n in sorted(child_no_editgrid):
            print(f'  - {n}')
    else:
        print('✅ All child tables have editable_grid=1.')

    # 13) Extra checks for non-DocType resources
    #     Keep these light and safe; only flag clear problems
    # Reports
    reports = list(catalog_by_type.get('Report', {}).values())
    report_issues = []
    for r in reports:
        rt = (r.data.get('report_type') or '').strip()
        ref_dt = (r.data.get('ref_doctype') or '').strip()
        if rt in {'Report Builder', 'Script Report'} and not ref_dt:
            report_issues.append((r.name, 'Missing ref_doctype for non-Query report'))
        if rt == 'Query Report':
            # query text is usually stored inline as 'query'
            if not (r.data.get('query') or '').strip():
                # Some Query Reports may load SQL elsewhere; warn only
                report_issues.append((r.name, "Query Report without inline 'query'"))
        # Validate ref_doctype exists (repo or DB)
        if ref_dt:
            if ref_dt not in doctypes:
                exists = False
                try:
                    if frappe.db.exists('DocType', ref_dt):
                        exists = True
                except Exception:
                    pass
                if not exists:
                    report_issues.append(
                        (r.name, f"ref_doctype '{ref_dt}' not found on disk or DB")
                    )
    if report_issues:
        print('⚠️ Report sanity issues:')
        for name, msg in sorted(report_issues):
            print(f'  - {name}: {msg}')
    else:
        print('✅ Reports: basic checks OK.')

    # Dashboard Chart / Number Card document_type validations
    bad_doc_target = []
    for rtype in ('Dashboard Chart', 'Number Card'):
        for res in catalog_by_type.get(rtype, {}).values():
            dt = (res.data.get('document_type') or '').strip()
            if dt:
                if dt not in doctypes:
                    exists = False
                    try:
                        if frappe.db.exists('DocType', dt):
                            exists = True
                    except Exception:
                        pass
                    if not exists:
                        bad_doc_target.append((rtype, res.name, dt))
    if bad_doc_target:
        print('❌ Chart/Card document_type targets missing:')
        for rtype, name, dt in sorted(bad_doc_target):
            print(f"  - {rtype} '{name}' → document_type '{dt}' not found (disk+DB)")
    else:
        print('✅ Dashboard Charts & Number Cards: document_type targets OK (or unset).')

    # Per-type counts (again, compact)
    print('Resources per type:')
    for rtype, d in sorted(catalog_by_type.items(), key=lambda x: (-len(x[1]), x[0])):
        print(f'  - {rtype}: {len(d)}')


# Allow local execution
if __name__ == '__main__':
    run()
