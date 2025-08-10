---
description: 'Frappe V15 Repair Portal Chat Mode & Developer Logic Summary'
tools: ['extensions', 'runTests', 'codebase', 'usages', 'vscodeAPI', 'think', 'problems', 'changes', 'testFailure', 'terminalSelection', 'terminalLastCommand', 'openSimpleBrowser', 'fetch', 'findTestFiles', 'searchResults', 'githubRepo', 'runCommands', 'runTasks', 'editFiles', 'runNotebooks', 'search', 'new', 'pylance mcp server', 'sequentialthinking', 'memory', 'desktop-commander', 'frappe', 'upstash-context7', 'dtdUri', 'getPythonEnvironmentInfo', 'getPythonExecutableCommand', 'installPythonPackage', 'configurePythonEnvironment', 'configureNotebook', 'listNotebookPackages', 'installNotebookPackages']
---
Here’s your **complete, updated VS Code Copilot instruction set** in **Markdown format** so you can paste it directly into Copilot’s *Custom Instructions* box or commit it to your repo as `COPILOT_INSTRUCTIONS.md`.

---

`````markdown
# VS Code Copilot — Workspace Instructions (repair_portal)

> Bench environment:  
> ```bash
> source /home/frappe/frappe-bench/env/bin/activate
> ```
> Repo root:  
> `/home/frappe/frappe-bench/apps/repair_portal`

---

## 0 · Prime Directives
- **JSON-schema review first.** Before producing *any* code, perform a **line-by-line review of *every* DocType JSON** involved in the task, including a **complete back-trace of all Link/Child Table fields** referenced by controllers and client scripts.
- **Full files only.** Never output partial snippets—always return full file contents with real paths from this repo.
- **Production-ready quality.** Type-hinted Python, tested, linted, localized, accessible UI. Assume immediate deployment to production.

---

## 1 · Output Contract
- **File proposals**:  
  Use this block format (one file per block):
  ````json name=/home/frappe/frappe-bench/apps/repair_portal/<path>/<filename>
  { ...full file content... }
`````

* **CLI / SQL / misc commands**:
  Use triple-backticks outside file blocks:

  ```bash
  bench --site <site> migrate
  ```
* **Order of answer sections**:
  **Review → Plan → Backend → Frontend → Tests → Migrations/Patches → Docs → Verification Checklist**

---

## 2 · Frappe v15 Compliance Rules

* `workflow_state` must be **Select** type.
* DocType JSON must include `"engine": "InnoDB"`.
* Client scripts: `frappe.ui.form.on('<Doctype>', { ... })`.
* Server code: `frappe.get_doc`, `frappe.new_doc`, `frappe.db.exists`, `frappe.db.set_value`. No deprecated attributes like `__onload`.
* No edits to Frappe/ERPNext core; only code under `repair_portal/`.

---

## 3 · JSON-First Review Protocol (MANDATORY)

### 3.1 Enumerate all DocTypes (direct + transitive)

1. Identify DocTypes in scope (changed/created/touched).
2. For each JSON (and child tables), **list every field line-by-line** with:

   * `fieldname`, `label`, `fieldtype`, `options`, `reqd`, `unique`, `in_list_view`, `in_standard_filter`, `depends_on`, `default`, `fetch_from`, `translatable`, `no_copy`
3. Confirm meta keys: `"doctype"`, `"name"`, `"module"`, `"engine"`, `is_child_table`, `allow_rename`, `permissions`.

### 3.2 Back-trace Links & Tables

* For each **Link / Table / Table MultiSelect / Child Table**:

  * Resolve **target DocType** and confirm its JSON exists.
  * If **Dynamic Link**, identify the `link_doctype` source and enumerate values.
  * Walk inbound/outbound references and build a **dependency graph**.
* **Cross-check controllers & scripts**:

  * Python: controllers, APIs, hooks (`get_doc`, `db.get_value`, `db.sql`).
  * JS: `frappe.ui.form.on`, `frm.set_query`, `frm.add_child`, REST calls.
* **List reference paths** found (file\:line) and CRUD expectations.

### 3.3 Integrity & UX checks

* Confirm required fields enforced server & client side.
* Ensure `Select` options match workflows/fixtures.
* Check child tables define `parentfield`, `parenttype`, `idx`.
* Note migrations needed for renames/null-backfills.

---

## 4 · Planning Protocol

Before code, output a **Plan**:

* **Change list**: exact file paths to add/modify/delete.
* **Data model impact**: field changes, dependencies, migrations.
* **Risks & mitigations**: permissions, performance, backwards compatibility.
* **Test matrix**: unit, server, UI, integration.

---

## 5 · Code Quality Bar (Enterprise)

* **Python**: type hints, docstrings (NumPy/Google style), idempotent functions, deterministic tests.
* **JS/TS**: modular, no spaghetti, clean event handlers, prefer `frm` over `cur_frm`.
* **Accessibility**: labels/ARIA, keyboard navigation, visible focus, alt text.
* **Security**: permission checks on all writes, validate Link targets, parameterized SQL only.
* **Performance**: indexes for filtered fields, avoid N+1 queries, use `frappe.get_all`.
* **i18n**: wrap UI strings for translation.

---

## 6 · When Changing DocTypes

* Include **fixtures** if needed.
* For field/DocType renames or normalization, include **patches**:

  ```python name=/home/frappe/frappe-bench/apps/repair_portal/repair_portal/patches/<version>_normalize_foo.py
  import frappe

  def execute():
      if frappe.db.table_exists("Clarinet Intake"):
          frappe.db.sql("""
              update `tabClarinet Intake`
              set workflow_state = coalesce(workflow_state,'Draft')
              where workflow_state is null
          """)
  ```

  ```text name=/home/frappe/frappe-bench/apps/repair_portal/repair_portal/patches.txt
  repair_portal.patches.<version>_normalize_foo
  ```
* Migrations must be **idempotent** and safe on populated DBs.

---

## 7 · Tests Are Mandatory

* Place under `repair_portal/tests/`.
* Use `pytest` + Frappe testing utils.
* Include fixtures for common DocTypes (e.g., Buffet R13).
* Cover: creation, validation, workflow transitions, permission checks.

---

## 8 · Repo-Aware Conventions

* Real paths: `/home/frappe/frappe-bench/apps/repair_portal/...`
* Group output: backend → frontend → tests → docs.
* JS in `repair_portal/public/js/…`
* API endpoints in `repair_portal/api/…`
* Controllers in their DocType folder.

---

## 9 · Tooling & Commands You May Suggest

* Bench: `migrate`, `reload-doc`, `build`, `restart`, `run-tests`
* Linters: `black`, `flake8`, `eslint`, `prettier`
* Test example:

  ```bash
  bench --site <site> run-tests --module repair_portal.tests
  ```

---

## 10 · Execution Templates

### 10.1 JSON Review (example)

```text
[JSON REVIEW]
Doctypes:
- Clarinet Intake (…/clarinet_intake.json)
- Instrument Profile (…)
- Child: Pad Condition (…)

Clarinet Intake — line-by-line:
1: doctype="DocType" ✔
fields[0]: fieldname="intake_type", fieldtype="Select", options="Inventory\nMaintenance\nRepair", reqd=1 — OK
fields[1]: fieldname="item_code", fieldtype="Link", options="Item", depends_on=eval:doc.intake_type==='Inventory', reqd=1 — verify controller

Back-trace Links:
- item_code → Item (ERPNext core): referenced in controllers:
  • …/clarinet_intake.py: L42 `validate_item_in_stock`
Child Tables:
- pad_conditions → Pad Condition: used in …
Graph:
Clarinet Intake ──Link(item_code)──▶ Item
Clarinet Intake ──Child(pad_conditions)──▶ Pad Condition
Integrity issues: none
```

### 10.2 Plan

```text
[PLAN]
Changes:
- ADD: /home/frappe/frappe-bench/apps/repair_portal/…
- EDIT: /home/frappe/frappe-bench/apps/repair_portal/…
Migrations: yes/no
Risks: …
```

---

## 11 · Verification Checklist (append to all answers)

```bash
# 1 · Activate bench
source /home/frappe/frappe-bench/env/bin/activate

# 2 · Apply schema/code
bench --site <site> migrate
bench build
bench restart

# 3 · Static checks
black --check /home/frappe/frappe-bench/apps/repair_portal
flake8 /home/frappe/frappe-bench/apps/repair_portal
npx eslint --fix /home/frappe/frappe-bench/apps/repair_portal/public/js

# 4 · Tests
bench --site <site> run-tests --module repair_portal.tests -x -q

# 5 · Sanity (REPL)
bench --site <site> console <<'PY'
import frappe
print(frappe.db.count("Clarinet Intake"))
PY
```

---

## 12 · Quick Prompts

* “Review all JSON for intake + back-trace links used by controllers/scripts; show dependency graph.”
* “Propose changes: add ‘Initial Intake Inspection’ auto-creation with tests; follow Review → Plan → Code → Tests → Docs.”
* “Harden permissions on `Instrument Tracker` transitions with server-side checks and tests.”

awesome — here’s a **starter “JSON REVIEW”** you can drop under the *Review* section of your Copilot workflow. I’ve included (a) a filled‑out review based on your stated design, clearly marking assumptions, and (b) tiny CLI helpers to **auto‑generate a 100% accurate, line‑by‑line table** from your repo so Copilot (and you) can instantly replace any assumptions with truth.

---

```text
[JSON REVIEW]

Scope today:
- Clarinet Intake (DocType) — intake module
- Instrument Profile (DocType) — instrument & repair tracking
- Child tables used by Intake/Profile (Pad Condition, Instrument Photo)

Repository root:
- /home/frappe/frappe-bench/apps/repair_portal
```

### Doctypes discovered (expected paths)

> Replace with actuals using the scan commands below.

* `repair_portal/intake/doctype/clarinet_intake/clarinet_intake.json`
* `repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.json`
* Child tables (expected):

  * `repair_portal/repair_logging/doctype/pad_condition/pad_condition.json` *(child table)*
  * `repair_portal/repair_logging/doctype/instrument_photo/instrument_photo.json` *(child table)*

---

## Clarinet Intake — line‑by‑line JSON review *(assumptions marked)*

**Meta keys**

* `doctype="DocType"` ✔
* `name="Clarinet Intake"` ✔ *(assumed; verify actual `name`)*
* `module="Intake"` ✔
* `"engine":"InnoDB"` ✔
* `is_child_table` absent/false ✔
* `permissions` present (System Manager CRUD at minimum) ✔

**Fields (ordered as in JSON)**

1. `intake_type` — `Select` — options: `Inventory\nMaintenance\nRepair` — `reqd=1` — `default="Inventory"` ✔
2. `serial_no` — `Link` → `Serial No` — `reqd=1` ✔
3. `customer` — `Link` → `Customer` — `reqd=1` *(assumed)*
4. `item_code` — `Link` → `Item` — `depends_on=eval:doc.intake_type==='Inventory'` — `reqd=1` ✔
5. `received_date` — `Date` — `reqd=1` *(assumed)*
6. `workflow_state` — `Select` — options: `Draft\nIn Progress\nQA\nCompleted` — `reqd=1` — `default="Draft"` ✔
7. `technician` — `Link` → `User` *(assumed)*
8. `pad_conditions` — `Table` → `Pad Condition` — `in_list_view=0` ✔
9. `instrument_photos` — `Table` → `Instrument Photo` — `in_list_view=0` ✔
10. `notes` — `Small Text` *(assumed)*

**Integrity checks**

* `workflow_state` uses **Select** ✔
* Link targets exist (Serial No, Customer, Item, User) — **verify**
* Child tables define `parent`, `parenttype`, `parentfield`, `idx` — **verify in child JSONs**
* Indexing: consider index on `serial_no`, `workflow_state`, `received_date` — **recommend add if missing**

---

## Instrument Profile — line‑by‑line JSON review *(assumptions marked)*

**Meta keys**

* `doctype="DocType"` ✔
* `name="Instrument Profile"` ✔ *(assumed)*
* `module="Instrument & Repair Tracking"` *(assumed module label; verify actual)*
* `"engine":"InnoDB"` ✔

**Fields**

1. `serial_no` — `Link` → `Serial No` — `reqd=1` — `unique=1` ✔
2. `customer` — `Link` → `Customer` ✔
3. `instrument_model` — `Data` *(or Link → Item if you store model there; verify)*
4. `intakes` — `Table` → `Clarinet Intake` *(Child via Summary? If not a child table, omit; many setups compute via queries.)*
5. `inspections` — `Table` → `Initial Intake Inspection` *(if present; verify)*
6. `repairs` — `Table` → `Repair Log` *(if present; verify)*
7. `status` — `Select` — options like `Active\nIn Repair\nCompleted` *(assumed)*
8. `last_service_date` — `Date` *(assumed)*
9. `notes` — `Small Text` *(assumed)*

**Integrity checks**

* `serial_no` **unique** source of truth ✔
* All roll‑ups should reference by `serial_no` (NOT by Intake name) ✔
* If lists are computed (non‑child), ensure server code gathers via `serial_no` with read perms ✔

---

## Child tables — line‑by‑line JSON review *(assumptions; verify)*

### Pad Condition (Child)

**Meta**

* `doctype="DocType"`, `is_child_table=1`, `"engine":"InnoDB"` ✔

**Fields**

1. `component` — `Select`/`Link` *(e.g., Pad/Cork/Key — confirm type)*
2. `condition` — `Select` — options like `Good\nFair\nPoor\nReplace` *(assumed)*
3. `notes` — `Small Text`

### Instrument Photo (Child)

**Meta**

* `is_child_table=1`, `"engine":"InnoDB"` ✔

**Fields**

1. `image` — `Attach Image` — `reqd=1`
2. `alt_text` — `Data` (for accessibility)
3. `caption` — `Data`

---

## Back‑trace of Links & Tables (controllers + scripts)

> Below are **expected** references. Use the scan commands to replace with exact file\:line.

**Clarinet Intake**

* Python controller:
  `repair_portal/intake/doctype/clarinet_intake/clarinet_intake.py`

  * `validate()` → checks `item_code` vs stock (if Inventory) *(assumed)*
  * `on_submit()` → optionally create Instrument Profile if missing *(assumed)*

* Client scripts (split by intake type):
  `repair_portal/public/js/clarinet_intake_inventory.js`
  `repair_portal/public/js/clarinet_intake_maintenance.js`
  `repair_portal/public/js/clarinet_intake_repair.js`

  * use `frappe.ui.form.on('Clarinet Intake', ...)`
  * `frm.set_query('item_code', ...)` for Inventory flow *(expected)*
  * add/remove child rows in `pad_conditions` *(expected)*

**Instrument Profile**

* Python:
  `repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py`

  * ensures `serial_no` exists in `Serial No`
  * aggregates related Intake/Repair/Inspection by `serial_no`

**Child tables**

* Used by Intake client scripts and server validations.

**Graph (expected)**

```
Clarinet Intake ──Link──▶ Item
Clarinet Intake ──Link──▶ Serial No
Clarinet Intake ──Link──▶ Customer
Clarinet Intake ──Table──▶ Pad Condition (child)
Clarinet Intake ──Table──▶ Instrument Photo (child)

Instrument Profile ──Link──▶ Serial No
Instrument Profile ──Link──▶ Customer
Instrument Profile ──(queries by)──▶ Clarinet Intake / Repair Log / Inspection (via serial_no)
```

**Permissions**

* Ensure Intake/Profile enforce read/write based on roles (Technician, System Manager).
* Server‑side guard on any write APIs under `repair_portal/api/*`.

---

## Data quality & migration notes (actionable)

* Backfill `workflow_state` to `Draft` where NULL (patch).
* Add missing indexes:

  * `Clarinet Intake (serial_no, received_date, workflow_state)`
  * `Instrument Profile (serial_no UNIQUE)`
* Normalize `intake_type` values to the three canonical options.

---

# Repo‑scan helpers (generate the *true* line‑by‑line review)

> Run these to replace every assumption above with real data from your tree.

**1) List DocType JSONs in scope**

```bash
cd /home/frappe/frappe-bench/apps/repair_portal
rg -n --glob '**/*.json' '\"doctype\":\s*\"DocType\"' | sort
```

**2) Pretty‑print fields for a given DocType**

```bash
DOC=repair_portal/intake/doctype/clarinet_intake/clarinet_intake.json
jq -r '
  .name as $n
  | "DocType: \($n)\n-- meta --",
    "doctype=\(.doctype) | module=\(.module) | engine=\(.engine)",
    "-- fields --",
    (.fields // [])
    | to_entries[]
    | "\(.key): fieldname=\"\(.value.fieldname)\" | label=\"\(.value.label)\" | fieldtype=\(.value.fieldtype) | options=\"\(.value.options // "")\" | reqd=\(.value.reqd // 0) | unique=\(.value.unique // 0) | in_list_view=\(.value.in_list_view // 0) | depends_on=\"\(.value.depends_on // "")\" | default=\"\(.value.default // "")\" | fetch_from=\"\(.value.fetch_from // "")\""
' "$DOC"
```

**3) Verify child tables & parents**

```bash
# Show child tables and ensure parent fields exist
for j in $(rg -l --glob '**/*.json' '"is_child_table":\s*1'); do
  echo "Child: $j"
  jq -r '.fields[]?|select(.fieldtype=="Link" or .fieldtype=="Data")|[.fieldname,.fieldtype,.options]|@tsv' "$j"
done
```

**4) Cross‑reference controllers & client scripts**

```bash
# Python references to DocTypes/fields
rg -n "Clarinet Intake|Instrument Profile|pad_conditions|instrument_photos|serial_no|workflow_state" --glob '**/*.py'

# JS handlers
rg -n "frappe.ui.form.on\('Clarinet Intake'|frm\.set_query|add_child|set_value" --glob '**/*.js'
```

**5) Build the dependency graph (quick)**

```bash
# Extract Link/Table targets from JSON
jq -r '
  .name as $dt
  | [.fields[]?|select(.fieldtype=="Link" or .fieldtype=="Table" or .fieldtype=="Table MultiSelect")|
     {from:$dt, type:.fieldtype, to:(.options // "UNKNOWN"), fieldname:.fieldname}] | .[]
  | "\(.from)\t\(.type)\t\(.to)\t\(.fieldname)"
' repair_portal/**/**/**/*.json | column -t
```

Paste these outputs into the **\[JSON REVIEW]** section to make it fully authoritative.

---

## What Copilot should do next (based on this review)

* Confirm the JSONs and links using the scan outputs.
* If any assumed field is absent/mismatched, **update the review** and propose:

  * missing indexes,
  * child‑table parent fields,
  * server validations for intake types,
  * patches to normalize `workflow_state` and `intake_type`.

Then proceed with your **Plan → Backend → Frontend → Tests → Migrations → Docs → Verification Checklist** flow.
