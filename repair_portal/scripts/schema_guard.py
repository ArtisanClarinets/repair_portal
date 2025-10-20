#!/usr/bin/env python3
import glob
import json
import os
import sys

ROOT = "/home/frappe/frappe-bench/apps/repair_portal"
errors = []


def load_jsons():
    files = glob.glob(f"{ROOT}/**/*.json", recursive=True)
    out = {}
    for f in files:
        # Skip node_modules directory
        if "node_modules" in f:
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                j = json.load(fh)
            if j.get("doctype") == "DocType":
                name = j.get("name") or os.path.basename(f).replace(".json", "")
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
        if ft in ("Link", "Table", "Table MultiSelect", "Dynamic Link"):
            refs.append((ft, fld.get("options", "UNKNOWN"), fld.get("fieldname", f"idx{i}"), path))
    return refs


def is_child(meta):
    return bool(meta.get("is_child_table", 0))


def main():
    metas = load_jsons()
    names = set(metas.keys())

    all_refs = []
    for name, (path, meta) in metas.items():
        check_engine(meta, path)
        if is_child(meta) and meta.get("is_submittable"):
            errors.append(f"[CHILD SUBMITTABLE] {path}: child tables must not be submittable")
        all_refs.extend(collect_refs(meta, path))

    core_allow = {
        "Item",
        "Customer",
        "Supplier",
        "Serial No",
        "User",
        "File",
        "Address",
        "Contact",
        "UOM",
        "Company",
        "Project",
        "ToDo",
        "Communication",
        "Workflow",
        "Workflow Action",
        "Workflow State",
    }
    for ft, target, fieldname, path in all_refs:
        if ft == "Dynamic Link":
            continue
        if target == "UNKNOWN" or not target.strip():
            errors.append(f"[REF OPTIONS] {path}: field '{fieldname}' type {ft} missing .options")
        elif target not in names and target not in core_allow:
            errors.append(f"[MISSING TARGET] {path}: field '{fieldname}' → '{target}' not found/whitelisted")

    if errors:
        print("❌ Schema Guard FAILED\n")
        for e in sorted(errors):
            print(e)
        sys.exit(1)
    print("✅ Schema Guard PASSED")


if __name__ == "__main__":
    main()
