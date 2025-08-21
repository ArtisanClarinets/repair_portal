#!/usr/bin/env python3
import json
import os
import re
from collections import defaultdict

root = "/home/frappe/frappe-bench/apps/repair_portal/repair_portal"
paths = []
for dirpath, dirnames, filenames in os.walk(root):
	if os.path.sep + "doctype" + os.path.sep in dirpath:
		for f in filenames:
			if f.endswith(".json"):
				paths.append(os.path.join(dirpath, f))
paths = sorted(paths)


def canon_compare_fieldname(s):
	if not s:
		return ""
	s = str(s)
	s = re.sub(r"[^0-9A-Za-z]+", "", s)  # remove non-alnum for strict compare
	return s.lower()


def canon_display_fieldname(s):
	if not s:
		return ""
	s = str(s).strip()
	s = re.sub(r"[^0-9A-Za-z]+", "_", s)
	s = re.sub(r"_+", "_", s)
	return s.lower().strip("_")


def canon_label(s):
	if not s:
		return ""
	return re.sub(r"\s+", " ", str(s).strip()).lower()


report = {
	"meta": {"root": root, "files_found": len(paths)},
	"files": {},
	"doctypes": {},
	"issues": [],
}

for p in paths:
	try:
		with open(p, encoding="utf-8") as f:
			data = json.load(f)
	except Exception as e:
		report["files"][p] = {"error": str(e)}
		continue
	name = data.get("name") or data.get("doctype") or os.path.splitext(os.path.basename(p))[0]
	fields = data.get("fields", [])
	report["files"][p] = {"name": name, "fields_count": len(fields)}
	dt = report["doctypes"].setdefault(name, {"paths": [], "fields": []})
	dt["paths"].append(p)
	for fld in fields:
		fn = fld.get("fieldname")
		lbl = fld.get("label")
		dt["fields"].append({"fieldname": fn, "label": lbl, "raw": fld, "path": p})

# duplicate doctypes
for dtname, dt in report["doctypes"].items():
	if len(dt["paths"]) > 1:
		report["issues"].append({"type": "duplicate_doctype_files", "doctype": dtname, "paths": dt["paths"]})

# per-doctype checks
for dtname, dt in report["doctypes"].items():
	by_fn_case = defaultdict(list)
	by_lbl_case = defaultdict(list)
	by_fn_canon = defaultdict(list)
	for f in dt["fields"]:
		fn = f.get("fieldname")
		lbl = f.get("label")
		if fn is not None:
			by_fn_case[fn.lower()].append({"fieldname": fn, "path": f["path"]})
			by_fn_canon[canon_compare_fieldname(fn)].append({"fieldname": fn, "path": f["path"]})
		if lbl is not None:
			by_lbl_case[lbl.lower()].append({"label": lbl, "path": f["path"]})
	# exact name duplicates (case-insensitive)
	for key, items in by_fn_case.items():
		if len(items) > 1:
			report["issues"].append(
				{
					"type": "intra_doctype_duplicate_fieldname_case_insensitive",
					"doctype": dtname,
					"fieldname_variant": key,
					"occurrences": items,
				}
			)
	# duplicate labels case-insensitive
	for key, items in by_lbl_case.items():
		if len(items) > 1:
			report["issues"].append(
				{
					"type": "intra_doctype_duplicate_label_case_insensitive",
					"doctype": dtname,
					"label_variant": key,
					"occurrences": items,
				}
			)
	# differing only by capitalization/underscores (canonical compare)
	for key, items in by_fn_canon.items():
		names = set(i["fieldname"] for i in items if i["fieldname"])
		if len(names) > 1:
			# suggest canonical name using display canonicalizer
			suggestion = canon_display_fieldname(sorted(names, key=lambda s: (len(s), s))[0])
			report["issues"].append(
				{
					"type": "intra_doctype_similar_fieldnames",
					"doctype": dtname,
					"canonical_compare": key,
					"names": list(names),
					"suggested_fieldname": suggestion,
					"occurrences": items,
				}
			)

# cross-doctype collisions
cross = defaultdict(list)
for dtname, dt in report["doctypes"].items():
	for f in dt["fields"]:
		fn = f.get("fieldname")
		lbl = f.get("label")
		cross[canon_compare_fieldname(fn)].append(
			{"doctype": dtname, "fieldname": fn, "label": lbl, "path": f["path"]}
		)
for key, items in cross.items():
	names = set(i["fieldname"] for i in items if i["fieldname"])
	doctypes = set(i["doctype"] for i in items)
	if len(items) > 1 and len(names) > 1:
		suggestion = canon_display_fieldname(sorted(names, key=lambda s: (len(s), s))[0])
		report["issues"].append(
			{
				"type": "cross_doctype_similar_fieldnames",
				"canonical_compare": key,
				"suggested_fieldname": suggestion,
				"count": len(items),
				"examples": items[:10],
			}
		)

# write report
out = os.path.join(root, ".doctype_audit_report.json")
with open(out, "w", encoding="utf-8") as f:
	json.dump(report, f, indent=2)
print("files_scanned", len(paths), "issues_found", len(report["issues"]))
print("report_written", out)
