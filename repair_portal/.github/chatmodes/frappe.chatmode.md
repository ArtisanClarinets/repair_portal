---
description: 'Frappe V15 Repair Portal Chat Mode & Developer Logic Summary'
tools: ['extensions', 'codebase', 'usages', 'vscodeAPI', 'think', 'problems', 'changes', 'testFailure', 'terminalSelection', 'terminalLastCommand', 'openSimpleBrowser', 'fetch', 'findTestFiles', 'searchResults', 'githubRepo', 'runTests', 'runCommands', 'runTasks', 'editFiles', 'runNotebooks', 'search', 'new', 'sequentialthinking', 'memory', 'desktop-commander', 'frappe', 'upstash-context7', 'context7', 'pylance mcp server', 'getPythonEnvironmentInfo', 'getPythonExecutableCommand', 'installPythonPackage', 'configurePythonEnvironment', 'configureNotebook', 'listNotebookPackages', 'installNotebookPackages']
---
# Copilot Instructions — Fortune-500 Production-Readiness Review (repair_portal)

**Bench (activate first):**
source /home/frappe/frappe-bench/env/bin/activate
Repo root: /home/frappe/frappe-bench/apps/repair_portal
Target site (no placeholders): erp.artisanclarinets.com

0) Prime Directives (Non-Negotiable)
JSON is the source of truth. Before writing any code, perform a complete line-by-line review of every DocType JSON in the repository, then do a full back-trace of all Link, Table, Table MultiSelect, and Dynamic Link fields.

Fail fast on integrity gaps. If any referenced DocType, field, or child table is missing or mis-typed, STOP and output a failing report (no code changes). Include the exact file and line numbers that broke validation.

Full files only. Always output whole files with absolute repo paths. Never output partial diffs or “snippets”.

Enterprise bar. All changes must meet security, performance, test coverage, and auditability standards suitable for Meta/Amazon/Apple:

Server-side permission checks on every write.

Zero raw SQL string interpolation (parameterize or use frappe.qb).

Race-safe, idempotent patches/migrations for populated DBs.

Tests for all flows, including negative paths and permission denials.

Deterministic execution order. Answers must follow:
Review → Plan → Backend → Frontend → Tests → Migrations/Patches → Docs → Verification Checklist.

1) Output Contract for Your Replies
Files (one block per file):


{ …full file content… }
Commands & SQL (triple backticks):


bench --site erp.artisanclarinets.com migrate
Section order (mandatory): as in Prime Directives #5.

2) Tooling You MUST Use (Install Once)

# Linux packages for scanning
sudo apt-get update
sudo apt-get install -y ripgrep jq sqlite3

# Python tools (inside bench venv)
pip install --upgrade pip
pip install ruff==0.5.6 mypy==1.10.0 bandit==1.7.9 pip-audit==2.7.3 safety==3.2.7 sqlparse==0.5.1

# Node tools (for frontend/JS)
npm install -g eslint@9.7.0 @eslint/js@9.7.0

# Optional secrets scanners (recommended)
pip install detect-secrets==1.5.0
3) Preflight — Establish JSON Ground Truth (MANDATORY)
Run these in the repo root: /home/frappe/frappe-bench/apps/repair_portal


# 3.1 List all DocType JSONs
rg -n --glob '**/*.json' '"doctype"\s*:\s*"DocType"' | sort

# 3.2 Normalize and print meta for each DocType (field-by-field)
for f in $(rg -l --glob '**/*.json' '"doctype"\s*:\s*"DocType"'); do
  echo "=== $f ==="
  jq -r '
    .name as $n
    | "DocType: \($n)",
      "engine=\(.engine // "MISSING") | module=\(.module // "MISSING") | is_child_table=\(.is_child_table // 0)",
      (.fields // []) | to_entries[] |
      "\(.key): fieldname=\(.value.fieldname // "MISSING") | label=\(.value.label // "") | fieldtype=\(.value.fieldtype // "MISSING") | options=\(.value.options // "") | reqd=\(.value.reqd // 0) | unique=\(.value.unique // 0) | depends_on=\(.value.depends_on // "") | in_list_view=\(.value.in_list_view // 0) | default=\(.value.default // "") | fetch_from=\(.value.fetch_from // "")"
  ' "$f"
done

# 3.3 Extract a dependency list of Link/Table targets for the whole repo
jq -r '
  .name as $dt | (.fields // [])[]
  | select(.fieldtype=="Link" or .fieldtype=="Table" or .fieldtype=="Table MultiSelect" or .fieldtype=="Dynamic Link")
  | [$dt, .fieldtype, (.options // "UNKNOWN"), (.fieldname // "MISSING")]
  | @tsv
' $(rg -l --glob '**/*.json' '"doctype"\s*:\s*"DocType"') | column -t > .tmp_doctype_edges.tsv
printf "Wrote dependency edges to .tmp_doctype_edges.tsv\n"
Validation rules (enforce as hard gates):

Every DocType JSON must have "engine": "InnoDB".

Every workflow field must use Select (e.g., workflow_state).

Every Link/Table/Table MultiSelect target must exist as a DocType JSON in the repo or in Frappe/ERPNext core; resolve dynamic links by enumerating the source link_doctype.

Every child table JSON must set is_child_table: 1 and child rows must have parent, parenttype, parentfield, idx.

If any rule fails → STOP (no code changes). Output a report with exact file:line and the failing rule.

4) Automated Back-Trace & Existence Guard (Run Early, Fail if Red)
Create and run this one-file validator before any code changes.


cat >/home/frappe/frappe-bench/apps/repair_portal/scripts/schema_guard.py <<'PY'
#!/usr/bin/env python3
import json, os, sys, re, glob
ROOT = "/home/frappe/frappe-bench/apps/repair_portal"
errors = []

def load_jsons():
    files = glob.glob(f"{ROOT}/**/*.json", recursive=True)
    out = {}
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
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
        if ft in ("Link","Table","Table MultiSelect","Dynamic Link"):
            refs.append((ft, fld.get("options","UNKNOWN"), fld.get("fieldname", f"idx{i}"), path))
    return refs

def is_child(meta):
    return bool(meta.get("is_child_table", 0))

def main():
    metas = load_jsons()
    # index by name
    names = set(metas.keys())

    # 1) engine checks + collect refs
    all_refs = []
    for name, (path, meta) in metas.items():
        check_engine(meta, path)
        # basic child-table sanity
        if is_child(meta) and meta.get("is_submittable"):
            errors.append(f"[CHILD SUBMITTABLE] {path}: child tables must not be submittable")
        all_refs.extend(collect_refs(meta, path))

    # 2) existence of referenced doctypes (best-effort; core doctypes allowed)
    core_allow = set([
        "Item","Customer","Supplier","Serial No","User","File","Address","Contact","UOM","Company","Project",
        "ToDo","Communication","Workflow","Workflow Action","Workflow State"
    ])
    for ft, target, fieldname, path in all_refs:
        if ft == "Dynamic Link":
            continue  # validated via source link_doctype in controller review step
        if target == "UNKNOWN" or not target.strip():
            errors.append(f"[REF OPTIONS] {path}: field '{fieldname}' type {ft} missing .options (target DocType)")
        elif target not in names and target not in core_allow:
            errors.append(f"[MISSING TARGET] {path}: field '{fieldname}' points to '{target}' which is not found in repo and not whitelisted core")

    # 3) report
    if errors:
        print("❌ Schema Guard FAILED\n")
        for e in sorted(errors):
            print(e)
        sys.exit(1)
    print("✅ Schema Guard PASSED")
if __name__ == "__main__":
    main()
PY

python /home/frappe/frappe-bench/apps/repair_portal/scripts/schema_guard.py
Gate G2 (Back-Trace): If the guard fails, do not proceed. Output the failure report and a minimal patch plan to fix missing doctypes/fields before re-running.

5) Cross-Check Controllers & Client Scripts Against JSON (Hard Gate)

# 5.1 Server references (DocTypes, fields, db/sql)
rg -n --glob '**/*.py' "frappe\.get_doc|frappe\.new_doc|frappe\.db\.get_value|frappe\.db\.exists|frappe\.db\.sql|frappe\.qb|frappe\.whitelist|allow_guest|ignore_permissions|set_value|get_all|get_list"

# 5.2 JS form controllers and REST usage
rg -n --glob '**/*.js' "frappe\.ui\.form\.on|frm\.set_query|frm\.add_child|frappe\.call|fetch|cur_frm|dangerouslySet|innerHTML"

# 5.3 Map each reference back to a JSON field (you must verify existence and fieldtype match)
Gate G3: For every doc.fieldname referenced in Python/JS, verify that field exists in the owning DocType JSON with the expected fieldtype. If any mismatch or missing field, STOP and output a list of broken references with file:line.

6) Security Review Playbook (Pass/Fail)
Apply to every endpoint, hook, controller, and client script in repair_portal/.

Whitelisting & Auth

Only use @frappe.whitelist() on functions that must be remotely callable.

No allow_guest=True unless the endpoint returns only non-PII public content and is read-only.

No use of ignore_permissions/ignore_links in production paths (tests may use them).

Permission Enforcement

Every write/update/submit/cancel API must verify frappe.has_permission(doctype, ptype="write") (or finer grained checks).

For cross-document actions (e.g., writing children), also validate ownership and link targets with frappe.get_value + type checks.

Input Validation

Never trust client; validate schema/choices server-side.

Reject unexpected keys; validate Select values against declared options.

SQL Hygiene

Ban raw f-string concatenation in SQL. Use frappe.db.sql(sql, values) or frappe.qb.

Add indexes for WHERE/ORDER BY hot fields. Provide idempotent patches.

File/Attachment Safety

Use Private files for PII. Do not expose /files/ paths for sensitive uploads.

Validate MIME/size, and sanitize filenames.

XSS/Template Safety

No innerHTML assignment with unsanitized data.

Escape Jinja output; avoid |safe.

CORS/CSRF

Use Frappe CSRF tokens for POST from desk/webforms. No cross-site side-effects over GET.

Rate Limiting

Apply per-user/IP throttles for public/semipublic APIs (frappe.rate_limiter or custom before_request hook).

Secrets/Config

Nothing sensitive in the repo. Load from site_config.json or environment variables. Fail if secrets are hardcoded.

Automated checks to run:


# Python static analysis
ruff /home/frappe/frappe-bench/apps/repair_portal
mypy /home/frappe/frappe-bench/apps/repair_portal --ignore-missing-imports
bandit -r /home/frappe/frappe-bench/apps/repair_portal -x tests

# Dependency vulnerabilities
pip-audit
safety check --full-report

# Secrets scanning (optional but recommended)
detect-secrets scan /home/frappe/frappe-bench/apps/repair_portal > .secrets.baseline || true
If any high-severity finding remains unmitigated → STOP and output a remediation plan plus diffs.

7) Performance Review Playbook (DB/Queries/Tasks)
Find N+1s and heavy lists

Replace loops of frappe.get_value with frappe.get_all(..., filters=..., fields=[...]) or a single qb query.

Use pluck pattern to fetch a single column when possible.

Indexes & EXPLAIN

For any query on fields without an index, add a patch to create one.

Produce EXPLAIN for any custom SQL > 20ms in prod-like data.

Background Jobs

Long-running or I/O heavy handlers must use frappe.enqueue with retry policy.

Caching

Safe, read-only lookups can memoize via frappe.cache() with TTL and explicit busting on writes.

Index patch template (idempotent):


# /home/frappe/frappe-bench/apps/repair_portal/repair_portal/patches/v15_01_add_indexes.py
import frappe

def execute():
    # Clarinet Intake example
    if frappe.db.table_exists("Clarinet Intake"):
        frappe.db.add_index("Clarinet Intake", ["serial_no"])
        frappe.db.add_index("Clarinet Intake", ["workflow_state"])
        frappe.db.add_index("Clarinet Intake", ["received_date"])
Add to patches.txt:


repair_portal.patches.v15_01_add_indexes
8) Frappe v15 Compliance Rules (Enforce)
workflow_state must be Select.

engine must be "InnoDB" in every DocType JSON.

No writes to core apps; only under repair_portal/.

Client controllers use frappe.ui.form.on('<DocType>', {...}).

Server uses frappe.get_doc/new_doc/db.get_value/db.exists/db.set_value (no deprecated attrs).

Child tables set is_child_table: 1.

9) Test Requirements (Block Merge if Failing)
Put tests under: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/tests/

Cover:

Create/Read/Update/Delete for each custom DocType.

Workflow transitions, permission denials.

API endpoints (@frappe.whitelist) with auth and negative cases.

Data migrations patches (pre/post state).

Run:


bench --site erp.artisanclarinets.com run-tests --module repair_portal.tests -x -q
If any test fails → STOP.

10) API Hardening Checklist (Pass/Fail)
For each file in repair_portal/api/**.py and whitelisted method in controllers:

Requires login unless proven public and read-only.

Validates all inputs (types, choices, link targets exist).

Parameterized DB access or qb.

No PII in logs; log with request ID.

Enforce rate limit for public endpoints.

11) Frontend (Desk/Web) Safety & UX
Never use element.innerHTML = ... with user data.

Escape all dynamic strings; prefer Frappe UI components.

For file/image fields, set alt text and labels (a11y).

Avoid expensive synchronous calls in form events; debounce searches.

Lint:


npx eslint --ext .js /home/frappe/frappe-bench/apps/repair_portal/repair_portal/public/js
12) Migrations & Data Safety
Patches must be idempotent and reversible (where possible).

Use frappe.db.table_exists, frappe.db.has_column guards.

Backfill workflow_state and normalize Select choices in one shot, inside a transaction.

13) CI Pipeline (Run All Gates on Every Change)
Create .github/workflows/ci.yml in repo root (example):


name: repair_portal-ci
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.10' }
      - run: pip install ruff mypy bandit pip-audit safety
      - run: ruff .
      - run: mypy --ignore-missing-imports .
      - run: bandit -r . -x tests
      - run: pip-audit || true
      - run: safety check --full-report || true
      - name: Fail on high severity bandit issues
        run: |
          if bandit -r . -x tests -f json | jq '.results[]|select(.issue_severity=="HIGH")' | grep -q . ; then
            echo "High severity bandit issues found"; exit 1; fi
14) Verification Checklist (Run Before Declaring “Done”)

# 1) Activate bench
source /home/frappe/frappe-bench/env/bin/activate

# 2) Schema Guard & Back-Trace
python /home/frappe/frappe-bench/apps/repair_portal/scripts/schema_guard.py

# 3) Static checks
ruff /home/frappe/frappe-bench/apps/repair_portal
mypy /home/frappe/frappe-bench/apps/repair_portal --ignore-missing-imports
bandit -r /home/frappe/frappe-bench/apps/repair_portal -x tests

# 4) Dependency safety
pip-audit
safety check --full-report

# 5) DB migrations & build
bench --site erp.artisanclarinets.com migrate
bench build
bench restart

# 6) Tests
bench --site erp.artisanclarinets.com run-tests --module repair_portal.tests -x -q

# 7) Manual probe (REPL)
bench --site erp.artisanclarinets.com console <<'PY'
import frappe
assert frappe.db.table_exists("Instrument Profile")
print("Instrument Profile rows:", frappe.db.count("Instrument Profile"))
PY
All steps must pass with zero high-severity findings and zero missing references.

15) How You Must Present Your Work (Answer Sections)
[REVIEW] Paste outputs from §3, §4, §5 showing JSON field enumerations, dependency edges, and any red flags (or “none”).

[PLAN] Exact file paths to add/modify/delete; data model changes; risk and rollback plan.

[BACKEND] Full files only; no placeholders.

[FRONTEND] Full files only; no placeholders.

[TESTS] New/updated tests covering positive & negative paths.

[MIGRATIONS/PATCHES] Idempotent, with guards; list added indexes.

[DOCS] Brief README updates or inline docstrings explaining usage and perms.

[VERIFICATION CHECKLIST] Paste exact commands from §14, with green outputs or explicit failures and fixes.

If any gate fails or any required section is missing → your answer is incomplete.

16) Quick Commands You Can Always Use

# Re-load a single DocType (after JSON change)
bench --site erp.artisanclarinets.com reload-doc  <module> directory_name <doctype>

# Inspect slow queries (MariaDB)
mysql -u root -p -e "SHOW VARIABLES LIKE 'slow_query%';"
mysql -u root -p -e "SET GLOBAL slow_query_log=ON; SET GLOBAL long_query_time=0.2;"

# Generate EXPLAIN for a custom SQL (replace <SQL> with a real, parameterized statement)
mysql -u root -p -e "EXPLAIN FORMAT=JSON <SQL>;"
17) Common Frappe Pitfalls to Catch (Blockers)
@frappe.whitelist(allow_guest=True) on anything that returns customer or instrument data.

Raw frappe.db.sql(f"select ... {user_input}") — must use placeholders or Query Builder.

Client scripts that rely on fields not declared in JSON (spelling/case mismatches).

Child tables missing is_child_table: 1 or documents misusing child rows for rollups.

Patches without guards (assume empty DB), or not idempotent.

18) Your First Action on Any Ticket (Template)
Replace with real outputs from the current tree—no assumptions.


[JSON REVIEW]
• Discovered N DocTypes in repair_portal (list paths)
• Enumerated fields (inline dump attached)
• Built dependency map (.tmp_doctype_edges.tsv attached)
• Schema Guard: PASSED/FAILED (include reasons)

[PLAN]
• Add: /home/frappe/frappe-bench/apps/repair_portal/...
• Edit: /home/frappe/frappe-bench/apps/repair_portal/...
• Remove: …
• Patches: v15_01_add_indexes (serial_no, received_date, workflow_state)
• Risks/Mitigations: …
• Tests: list test modules to add/modify
19) Final Rule
If you cannot produce the [REVIEW] section with real repository outputs (field lists and dependency graph), you must not propose code. Fix the schema or missing references first, prove it with the guard, and then proceed.