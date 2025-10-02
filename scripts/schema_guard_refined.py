#!/usr/bin/env python3
import json, os, sys, glob

ROOT = "/home/frappe/frappe-bench/apps/repair_portal/repair_portal"
errors = []
warnings = []

def load_jsons():
    pattern = f"{ROOT}/**/doctype/**/*.json"
    files = glob.glob(pattern, recursive=True)
    out = {}
    for f in files:
        if '/node_modules/' in f or '/public/node_modules/' in f:
            continue
        try:
            with open(f, "r", encoding="utf-8") as fh:
                j = json.load(fh)
            if j.get("doctype") == "DocType":
                name = j.get("name")
                if name:
                    out[name] = (f, j)
        except Exception as e:
            errors.append(f"[JSON PARSE] {f}: {e}")
    return out

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
    return bool(meta.get("istable", 0) or meta.get("is_child_table", 0))

def main():
    metas = load_jsons()
    names = set(metas.keys())
    
    print(f"✓ Found {len(names)} DocTypes in repair_portal\n")

    all_refs = []
    for name, (path, meta) in metas.items():
        check_engine(meta, path)
        if is_child(meta) and meta.get("is_submittable"):
            errors.append(f"[CHILD SUBMITTABLE] {path}: child tables must not be submittable")
        all_refs.extend(collect_refs(meta, path))

    core_allow = set([
        "Item","Customer","Supplier","Serial No","User","File","Address","Contact","UOM","Company","Project",
        "ToDo","Communication","Workflow","Workflow Action","Workflow State","Sales Invoice","Purchase Order",
        "Stock Entry","Delivery Note","Payment Entry","Journal Entry","Warehouse","Item Group","Brand",
        "Email Group Member","Email Group","Lead","Opportunity","Purchase Receipt","Work Order","Currency",
        "Employee","DocType","Activity Type","Role","Service Type","Workshop","Price List","Asset",
        "Inspection Report","External Work Logs"
    ])
    
    for ft, target, fieldname, path in all_refs:
        if ft == "Dynamic Link":
            continue
        if target == "UNKNOWN" or not target.strip():
            errors.append(f"[REF OPTIONS] {path}: field '{fieldname}' type {ft} missing .options (target DocType)")
        elif target not in names and target not in core_allow:
            warnings.append(f"[MISSING TARGET] {path}: field '{fieldname}' points to '{target}' (not in repo, may be custom/external)")

    # Focus on player_profile
    player_profile_issues = [e for e in errors + warnings if 'player_profile' in e.lower()]
    if player_profile_issues:
        print("⚠️  Player Profile Module Issues:\n")
        for issue in player_profile_issues:
            print(f"  {issue}")
        print()

    if errors:
        print("❌ Schema Guard FAILED (critical errors)\n")
        for e in sorted(errors)[:20]:  # Show first 20
            print(e)
        sys.exit(1)
    elif warnings:
        print(f"⚠️  Schema Guard PASSED with {len(warnings)} warnings\n")
        sys.exit(0)
    else:
        print("✅ Schema Guard PASSED (no errors)")
        sys.exit(0)

if __name__ == "__main__":
    main()
