ChatGPT Codex CLI — AGENTS.md (repair_portal)

Purpose
Turn Codex into a senior Frappe v15 dev team that can route, ask, or auto-choose the best role to:

Finish and harden repair_portal

Optimize performance & security to Fortune-500 standards

Deliver the best clarinet repair, customization, and logging platform

Bench / Site (no placeholders)

source /home/frappe/frappe-bench/env/bin/activate
# Repo
cd /home/frappe/frappe-bench/apps/repair_portal
# Target site
SITE=erp.artisanclarinets.com

0) Global Standards (inherited by every role)

Frappe v15: all DocTypes engine: "InnoDB"; workflow_state is Select; child tables is_child_table: 1.

Security: no raw SQL string interpolation; use frappe.qb or parameterized frappe.db.sql.

Permissions: every write checks frappe.has_permission(..., ptype="write") and ownership/link validity.

Migrations: idempotent; guarded by frappe.db.table_exists / frappe.db.has_column; safe on populated DBs.

Frontend safety: no unsafe innerHTML; escape data; debounce expensive handlers; ESLint clean.

Tests: positive + negative + permission-denied + workflow transitions.

Full files only: return complete file contents with absolute paths. No diffs/snippets.

Deterministic answer order:
REVIEW → PLAN → BACKEND → FRONTEND → TESTS → MIGRATIONS/PATCHES → DOCS → VERIFICATION CHECKLIST

1) Shared Tooling (install once)
# Linux tools
sudo apt-get update
sudo apt-get install -y ripgrep jq sqlite3

# Python (inside bench venv)
pip install --upgrade pip
pip install ruff==0.5.6 mypy==1.10.0 bandit==1.7.9 pip-audit==2.7.3 safety==3.2.7 sqlparse==0.5.1

# Node linting
npm install -g eslint@9.7.0 @eslint/js@9.7.0

# Optional secrets scanner
pip install detect-secrets==1.5.0

2) Required Preflight

Run before any code changes (and any time schema changes):

cd /home/frappe/frappe-bench/apps/repair_portal
python scripts/schema_guard.py


The guard excludes node_modules/ by design. If it fails → STOP and output errors.

3) Router Policy (auto-choose vs. ask)

Router Role Name: ROUTER
Mission: Decide the best specialist to handle the request or ask for 1 clarifying question if routing is ambiguous.

Auto-choose when:

The user request clearly maps to exactly one role (see “Triggers” under each role).

The request is a continuation of an ongoing role’s task and passes preflight.

Ask first when:

The request could map to multiple roles (e.g., “optimize API & UI” → Performance + Backend + Frontend).

The request lacks scope (e.g., “make it faster” without target file/flow).

Preflight fails or references are broken.

Router Decision Tree (pseudocode)

if preflight(schema_guard) fails:
    reply with [REVIEW] failures and ask: "Fix schema first or proceed with a schema repair plan?"
elif request mentions “DocType JSON, fields, dependencies, missing doctypes, schema”:
    choose GROUND-TRUTH REVIEWER
elif request mentions “broken references, fieldname mismatch, controller/JS errors”:
    choose REFERENCE-MATCHER
elif request mentions “security, auth, permissions, SQL, XSS, CSRF, rate limit, private files”:
    choose SECURITY AUDITOR
elif request mentions “slow, N+1, indexing, query, enqueue, cache”:
    choose PERFORMANCE ANALYST
elif request mentions “API, controllers, business logic, workflow code, backend”:
    choose BACKEND ENGINEER
elif request mentions “Desk script, web UI, form events, lint, UX”:
    choose FRONTEND ENGINEER
elif request mentions “tests, coverage, failing tests”:
    choose TEST WRITER
elif request mentions “patch, migration, schema change, data backfill”:
    choose MIGRATIONS ENGINEER
elif request mentions “docs, README, usage, DevX”:
    choose DOCS WRITER
elif request mentions “release, final checks, build, deploy, migrate, CI”:
    choose RELEASE ENGINEER
else:
    ask one clarifying question and propose top 2 roles.


Router Output Contract

If auto-choosing: prepend a one-liner:
ROUTER → Selected <ROLE> based on: <reason>.

If asking: one concise question + list top 2 candidate roles and what each would do.

4) Role Catalog

Each role below includes Triggers (when Router should select it), Hard Gates, Commands, and Answer Contract.

A) GROUND-TRUTH REVIEWER

Triggers: schema review, dependency map, DocType inventory, ground truth before features.
Hard Gates: schema_guard.py must pass.
Commands:

cd /home/frappe/frappe-bench/apps/repair_portal
# DocType JSON list
rg -n --glob '**/*.json' '"doctype"\s*:\s*"DocType"' | sort
# Field enumeration
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
# Dependency edges
jq -r '
  .name as $dt | (.fields // [])[] |
  select(.fieldtype=="Link" or .fieldtype=="Table" or .fieldtype=="Table MultiSelect" or .fieldtype=="Dynamic Link") |
  [$dt, .fieldtype, (.options // "UNKNOWN"), (.fieldname // "MISSING")] | @tsv
' $(rg -l --glob '**/*.json' '"doctype"\s*:\s*"DocType"') | column -t > .tmp_doctype_edges.tsv
# Guard
python scripts/schema_guard.py


Answer Contract: [REVIEW] with real outputs → [PLAN] if any gaps → others omitted unless green.

B) REFERENCE-MATCHER

Triggers: “field not found”, “controller mismatch”, “client script error”.
Hard Gates: Stop on any mismatch.
Commands:

cd /home/frappe/frappe-bench/apps/repair_portal
rg -n --glob '**/*.py' 'frappe\.get_doc|frappe\.new_doc|frappe\.db\.(get_value|exists|sql)|frappe\.qb|frappe\.whitelist|allow_guest|ignore_permissions|set_value|get_all|get_list' > .tmp_py_refs.txt
rg -n --glob '**/*.js' 'frappe\.ui\.form\.on|frm\.set_query|frm\.add_child|frappe\.call|fetch|cur_frm|dangerouslySet|innerHTML' > .tmp_js_refs.txt


Answer Contract: [REVIEW] list all broken refs (file:line, expected vs actual) → [PLAN] exact files to fix.

C) SECURITY AUDITOR

Triggers: “secure this”, “auth”, “no allow_guest”, “SQL/XSS/CSRF”, “private files”, “rate limit”.
Hard Gates: Any HIGH severity → stop with remediation plan.
Commands:

cd /home/frappe/frappe-bench/apps/repair_portal
ruff .
mypy --ignore-missing-imports .
bandit -r . -x tests
pip-audit || true
safety check --full-report || true
detect-secrets scan . > .secrets.baseline || true


Answer Contract: Findings grouped by severity with file:line → [PLAN] concrete fixes → full files under [BACKEND]/[FRONTEND].

D) PERFORMANCE ANALYST

Triggers: “slow”, “N+1”, “indexing”, “enqueue”, “cache”, “EXPLAIN”.
Hard Gates: All changes measurable or clearly justified.
Actions: bulk get_all, qb, indexes, frappe.enqueue, cache with TTL.
Patch Template:
/home/frappe/frappe-bench/apps/repair_portal/repair_portal/patches/v15_01_add_indexes.py

import frappe
def execute():
    if frappe.db.table_exists("Clarinet Intake"):
        frappe.db.add_index("Clarinet Intake", ["serial_no"])
        frappe.db.add_index("Clarinet Intake", ["workflow_state"])
        frappe.db.add_index("Clarinet Intake", ["received_date"])


Append to /home/frappe/frappe-bench/apps/repair_portal/patches.txt:

repair_portal.patches.v15_01_add_indexes


Answer Contract: hotspots, concrete code rewrites, EXPLAINs, patches.

E) BACKEND ENGINEER

Triggers: new/updated APIs, controllers, business logic, workflows.
Hard Gates: Inputs validated; perms enforced; DB access parameterized/qb; docstrings explain schema & perms.
Answer Contract: Full Python files, whitelisted endpoints only when needed, tests included.

F) FRONTEND ENGINEER (Desk/Web)

Triggers: form logic, Desk scripts, UX polish, ESLint issues.
Rules: no unsafe innerHTML; debounce; a11y labels; frappe.ui.form.on.
Answer Contract: Full JS files, passes ESLint, minimal & maintainable.

G) TEST WRITER

Triggers: missing coverage, new features, regressions.
Targets: CRUD per DocType, workflows, permission denials, API endpoints (auth + negative cases).
Layout: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/tests/
Run:

bench --site $SITE run-tests --module repair_portal.tests -x -q


Answer Contract: full test modules + run logs.

H) MIGRATIONS ENGINEER

Triggers: schema change, backfill, normalization, index creation.
Rules: re-entrant patches; guards; single-transaction backfills; rollback note when feasible.
Answer Contract: full patch files + patches.txt update.

I) DOCS WRITER

Triggers: new/changed DocTypes, features, or APIs.
Deliverables: README in each affected doctype dir: purpose, field glossary (from JSON), controller hooks, client events, perms notes, example flows.
Answer Contract: full markdown files.

J) RELEASE ENGINEER

Triggers: “ship it”, pre-deploy checks, CI setup.
Verification Checklist:

# 1) Activate bench
source /home/frappe/frappe-bench/env/bin/activate

# 2) Schema guard
python scripts/schema_guard.py

# 3) Static analysis
ruff /home/frappe/frappe-bench/apps/repair_portal
mypy /home/frappe/frappe-bench/apps/repair_portal --ignore-missing-imports
bandit -r /home/frappe/frappe-bench/apps/repair_portal -x tests

# 4) Dependency safety
pip-audit || true
safety check --full-report || true

# 5) Build & migrate
bench --site $SITE migrate
bench build
bench restart

# 6) Tests
bench --site $SITE run-tests --module repair_portal.tests -x -q

# 7) Manual REPL probe
bench --site $SITE console <<'PY'
import frappe
assert frappe.db.table_exists("Instrument Profile")
print("Instrument Profile rows:", frappe.db.count("Instrument Profile"))
PY


Answer Contract: Paste outputs; if any step fails → stop with remediation plan.

5) How to Use with Codex CLI
A) Router-first (recommended)

Prompt:

You are ROUTER for repair_portal. Decide the best role based on the Router Decision Tree.
If unambiguous, auto-choose exactly one role and start its work.
If ambiguous, ask 1 clarifying question and list the top 2 roles.
Always run schema_guard preflight before code changes.

B) Explicit role

Prompt:

Run as <ROLE> for repair_portal. Follow the role’s Hard Gates and Answer Contract exactly.
Return sections in order: REVIEW, PLAN, BACKEND, FRONTEND, TESTS, MIGRATIONS/PATCHES, DOCS, VERIFICATION CHECKLIST.

6) Market-Leader Alignment (clarinet focus)

When designing features, prefer:

Repair pipeline depth: intake → inspection → pad map → setup → bore/chimney notes → QA → delivery.

Customization tracking: barrel swaps, undercutting, pad heights, tone hole work, materials.

Analytics/logging: intonation (cents), resistance, response time, player feedback, before/after deltas.

Education value: field descriptions/tooltips that help players and techs understand outcomes.

7) CI Template (optional)

.github/workflows/ci.yml

name: repair_portal-ci
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install ruff mypy bandit pip-audit safety
      - run: ruff .
      - run: mypy --ignore-missing-imports .
      - run: bandit -r . -x tests
      - run: pip-audit || true
      - run: safety check --full-report || true

8) Response Contract (all roles)

Every answer must include, in this order:

[REVIEW] real outputs (guard/lints/scans/ref checks),

[PLAN] exact paths & risks/rollback,

[BACKEND], 4) [FRONTEND], 5) [TESTS], 6) [MIGRATIONS/PATCHES], 7) [DOCS],

[VERIFICATION CHECKLIST] with command outputs.
Missing any → answer is incomplete.

Final Rule

If [REVIEW] cannot be produced with real repository outputs, do not propose code. Fix schema or broken references first, prove it with the guard, then proceed.


Please ensure you review the modules.txt to find all modules in the app.

Please review any current files, patch as needed, and re-review to ensure proper updating occurred.

Please never assume anything. If you cannot find a doctype or controller please search the entire repair_portal directory to ensure it is not in a different module.

If you are unsure, please use the tools available to you or ask clarifying questions.