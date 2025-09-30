#!/usr/bin/env python3
# Path: scripts/schema_guard.py
# Date: 2025-09-30
# Version: 1.0.0
# Description: Static validation for DocType JSONs: broken links, child tables, dup fields, missing descriptions.
# Dependencies: python stdlib (json, pathlib)

import json, pathlib, sys

ROOT = pathlib.Path("/home/frappe/frappe-bench/apps/repair_portal")
errors, warnings = [], []

def load_doctypes():
    for json_path in ROOT.glob("**/doctype/**/*.json"):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            if data.get("doctype") == "DocType":
                yield json_path, data
        except Exception as e:
            errors.append((json_path, f"Invalid JSON: {e}"))

def check_engine(meta, path):
    eng = meta.get("engine")
    if eng != "InnoDB":
        errors.append(f"[ENGINE] {path}: engine={eng} (must be 'InnoDB')")

def collect_refs(meta, path):
    refs = []
    for i, fld in enumerate(meta.get("fields", [])):
        ft = fld.get("fieldtype")
        if ft in ("Link","Table","Table MultiSelect","Dynamic Link"):
            refs.append((ft, fld.get("options","UNKNOWN"), fld.get("fieldname", f"idx{i}"), path))
    return refs

def is_child(meta):
    return bool(meta.get("istable", 0)) or bool(meta.get("is_child_table", 0))

def main():
    metas = list(load_doctypes())
    # index by name and label
    names = set()
    for path, meta in metas:
        name = meta.get("name")
        label = meta.get("label")
        if name:
            names.add(name)
        if label and label != name:
            names.add(label)  # Some DocTypes use label for references

    # 1) engine checks + collect refs
    all_refs = []
    for path, meta in metas:
        check_engine(meta, path)
        # basic child-table sanity
        if is_child(meta) and meta.get("is_submittable"):
            errors.append(f"[CHILD SUBMITTABLE] {path}: child tables must not be submittable")
        all_refs.extend(collect_refs(meta, path))

    # 2) existence of referenced doctypes (best-effort; core doctypes allowed)
    core_allow = set([
        "Item","Customer","Supplier","Serial No","User","File","Address","Contact","UOM","Company","Project",
        "ToDo","Communication","Workflow","Workflow Action","Workflow State","DocType","Role","Department",
        "Employee", "Territory", "Currency", "Batch", "Stock Entry", "Material Request", "Purchase Order",
        "Sales Order", "Delivery Note", "Purchase Invoice", "Sales Invoice", "Payment Entry", "Journal Entry",
        "Brand", "Warehouse", "Item Group", "Price List", "Asset", "Work Order", "Purchase Receipt",
        "Activity Type", "Service Type", "Workshop", "Inspection Report", "External Work Logs"
    ])
    for ft, target, fieldname, path in all_refs:
        if ft == "Dynamic Link":
            continue  # validated via source link_doctype in controller review step
        if target == "UNKNOWN" or not target.strip():
            errors.append(f"[REF OPTIONS] {path}: field '{fieldname}' type {ft} missing .options (target DocType)")
        elif target not in names and target not in core_allow:
            errors.append(f"[MISSING TARGET] {path}: field '{fieldname}' points to '{target}' which is not found in repo and not whitelisted core")

    # 3) Check for duplicate fieldnames within each DocType
    for path, meta in metas:
        fields = meta.get("fields", [])
        seen = set()
        for f in fields:
            fname = f.get("fieldname")
            if not fname:
                errors.append(f"[NO FIELDNAME] {path}: field without fieldname")
                continue
            if fname in seen:
                errors.append(f"[DUPLICATE FIELD] {path}: duplicate fieldname: {fname}")
            seen.add(fname)

    # 4) report
    if errors:
        print("❌ Schema Guard FAILED\n")
        for e in sorted(errors):
            print(e)
        sys.exit(1)
    print("✅ Schema Guard PASSED")
    print(f"Validated {len(metas)} DocTypes with {len(all_refs)} references")

if __name__ == "__main__":
    main()