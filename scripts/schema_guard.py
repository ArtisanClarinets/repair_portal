#!/usr/bin/env python3
import json, os, sys, re, glob

ROOT = "repair_portal"
errors = []


def load_jsons():
    # Focus only on doctype folders and exclude bundled data, node_modules, test data
    patterns = [
        f"{ROOT}/**/doctype/**/*.json",
    ]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))

    out = {}
    for f in files:
        # Skip data files, templates, and test data - be more specific with patterns
        skip_patterns = [
            "bundled",
            "node_modules",
            "/templates/",
            "/test/",
            "/spec/",
            "/mock",
            "test.json",
            "spec.json",
        ]
        if any(skip in f for skip in skip_patterns):
            continue
        try:
            with open(f, "r", encoding="utf-8") as fh:
                j = json.load(fh)
            if isinstance(j, dict) and j.get("doctype") == "DocType":
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
    # Also create case-insensitive versions
    names_case_insensitive = {name.lower(): name for name in names}

    all_refs = []
    for name, (path, meta) in metas.items():
        check_engine(meta, path)
        if is_child(meta) and meta.get("is_submittable"):
            errors.append(f"[CHILD SUBMITTABLE] {path}: child tables must not be submittable")
        all_refs.extend(collect_refs(meta, path))

    core_allow = set(
        [
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
            "Item Group",
            "Warehouse",
            "Price List",
            "Quotation",
            "Sales Order",
            "Purchase Order",
            "Delivery Note",
            "Purchase Receipt",
            "Payment Entry",
            "Journal Entry",
            "DocType",
            "Currency",
            "Employee",
            "Role",
            "Activity Type",
            "Service Type",
            "Workshop",
            "Asset",
            "Stock Entry",
            "Work Order",
            "Inspection Report",
            "Brand",
            "Clarinet Intake",
            "Country",
            "Email Group",
            "Quality Inspection",
            "Attachment Entry",
            "Sales Invoice",
            "Subscription",
            "Material Request",
        ]
    )

    # Combine both repo doctypes and core allowed
    all_allowed = names.union(core_allow)

    for ft, target, fieldname, path in all_refs:
        if ft == "Dynamic Link":
            continue
        if target == "UNKNOWN" or not target.strip():
            errors.append(
                f"[REF OPTIONS] {path}: field '{fieldname}' type {ft} missing .options (target DocType)"
            )
        elif target not in all_allowed:
            # Try case-insensitive match for typos
            target_lower = target.lower()
            if target_lower in names_case_insensitive:
                actual_name = names_case_insensitive[target_lower]
                errors.append(
                    f"[CASE MISMATCH] {path}: field '{fieldname}' points to '{target}' but should be '{actual_name}'"
                )
            else:
                errors.append(
                    f"[MISSING TARGET] {path}: field '{fieldname}' points to '{target}' which is not found in repo and not whitelisted core"
                )

    if errors:
        print("❌ Schema Guard FAILED\n")
        for e in sorted(errors):
            print(e)
        sys.exit(1)
    print("✅ Schema Guard PASSED")


if __name__ == "__main__":
    main()
