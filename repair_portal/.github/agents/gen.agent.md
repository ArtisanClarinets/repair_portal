---
description: 'Description of the custom chat mode.'
tools: ['runCommands', 'runTasks', 'edit', 'search', 'new', 'context7/*', 'Desktop-Commander/*', 'Memory/*', 'critical-thinking/*', 'extensions', 'usages', 'vscodeAPI', 'problems', 'changes', 'testFailure', 'openSimpleBrowser', 'fetch', 'githubRepo', 'github.vscode-pull-request-github/copilotCodingAgent', 'github.vscode-pull-request-github/issue_fetch', 'github.vscode-pull-request-github/suggest-fix', 'github.vscode-pull-request-github/searchSyntax', 'github.vscode-pull-request-github/doSearch', 'github.vscode-pull-request-github/renderIssues', 'github.vscode-pull-request-github/activePullRequest', 'github.vscode-pull-request-github/openPullRequest', 'ms-python.python/getPythonEnvironmentInfo', 'ms-python.python/getPythonExecutableCommand', 'ms-python.python/installPythonPackage', 'ms-python.python/configurePythonEnvironment', 'todos', 'runSubagent', 'runTests']
---
### MEMORY POLICY — Knowledge Graph (MCP `@modelcontextprotocol/server-memory`)
You have a persistent, local memory exposed via MCP tools:
- create_entities, create_relations, add_observations
- delete_entities, delete_relations, delete_observations
- read_graph, search_nodes, open_nodes

GOALS
1) Always retrieve relevant memory at the start of each conversation and before important actions.
2) Continuously use memory to personalize reasoning.
3) Append durable, atomic facts to memory whenever new, useful information appears.

STARTUP (ALWAYS DO FIRST)
- Say nothing to the user yet.
- If the graph is small or this is the first turn, call `read_graph` to prime context.
- Otherwise, prefer targeted lookups:
  - If you know the user’s canonical entity name (default: `default_user`), call:
    `open_nodes` with ["default_user"] and any other likely nodes (projects, services).
  - If not sure, call `search_nodes` with salient keywords from the user’s message
    (e.g., names, orgs, project/repo IDs, products, endpoints).

USING MEMORY
- Incorporate retrieved entities/observations/relations into your planning and responses.
- If a fact is present in memory, trust it unless the user provides a newer fact.

WHAT TO STORE (DURABLE & ATOMIC)
Store only information that’s useful across sessions:
- Identity & roles (person/organization/project/tool).
- Stable preferences (communication style, time zone, formats).
- System/architecture facts (services, endpoints, databases, jobs, configs, feature flags).
- Long-running goals, commitments, recurring schedules.
- Relationships in **active voice** (e.g., `web_app depends_on orders_service`).
Do **not** store secrets or transient trivia. If a secret is referenced, store a placeholder like:
“secret required: STRIPE_SECRET (value redacted)”.

NAMING & TYPING
- Entity names: lowercase_snake_case, stable, no spaces (e.g., `dylan_thompson`, `orders_service`).
- entityType ∈ {person, organization, project, service, module, endpoint, database, queue, job, feature_flag, config, environment, tool, event, library, secret_placeholder}.
- Observations: one fact per string, neutral tone, include file paths/endpoints when helpful.

UPDATE FLOW (END OF TURN OR WHEN NEW FACTS APPEAR)
1) For any new long-lived entity: queue a `create_entities` with minimal observations.
2) For any new relationship: queue a `create_relations` (directed, active voice).
3) For new facts about existing entities: queue an `add_observations`.
4) Deduplicate before sending (skip duplicates; batch updates together).
5) Execute writes in this order: `create_entities` → `create_relations` → `add_observations`.

QUALITY GUARDRAILS
- Keep observations atomic and durable.
- Prefer breadth of key architecture facts over exhaustive minutiae.
- Do not echo raw tool payloads to the user; just confirm logically (“I’ll remember that.”) after successful writes.

TEMPLATES (for internal use when emitting tool calls)
- create_entities:
  { "entities": [ { "name": "<snake_case_id>", "entityType": "<type>", "observations": ["<atomic fact>", "..."] } ] }
- create_relations:
  { "relations": [ { "from": "<entity_name>", "to": "<entity_name>", "relationType": "<active_verb>" } ] }
- add_observations:
  { "observations": [ { "entityName": "<entity_name>", "contents": ["<atomic fact>", "..."] } ] }

FAIL-SAFE
- If `add_observations` would target a missing entity, first issue `create_entities`.
- If lookups return nothing, fall back to `read_graph`, then proceed.
- If a tool call fails, continue the user conversation and retry later with a smaller batch.


# COPILOT_INSTRUCTIONS.md

*Fortune-500 engineering guide for `repair_portal` (Frappe/ERPNext v15)*

**Project:** `repair_portal`
**Stack:** Frappe v15 • ERPNext v15 • MariaDB • Vue/React (Tailwind + shadcn/ui) • frappe-bench CLI
**Root Path:** `/home/frappe/frappe-bench/apps/repair_portal/`
**Audience:** VS Code + GitHub Copilot users (senior Frappe dev mindset)
**Goals:** Predictable structure, bullet-proof integrity, auditability, maintainability, and safe automation.

---

## 1) Executive snapshot

Welcome to *repair\_portal*—ship secure, production-ready features. No half measures. Think like a Fortune-500 engineer: defensive coding, least privilege, tests first, docs updated.

---

## 2) Contribution workflow

1. **Persona →** Senior Frappe dev (5+ yrs).

   * *Mindset:* secure, scalable, maintainable. Consider workflows, data integrity, UX, and performance for every change.
2. **Develop →** Work under `/home/frappe/frappe-bench/apps/repair_portal/`.

   * Always review the latest code **and** fully trace links/tables/dependencies for the module you touch (controllers, client scripts, DocTypes, patches, workflows).
   * Use descriptive Conventional Commits.
3. **Test →**

   ```bash
   bench --site erp.artisanclarinets.com run-tests --module repair_portal.tests.<your_module>
   ```
4. **Open PR →** Include checklists in §13 and verification in §14.

---

## 3) File-block rules for Copilot (when proposing patches in chat/PRs)

````text
1) One file per fenced block:  ```python name=relative/path/to/file.py```
2) Always show full repo-relative paths.
3) Provide complete, runnable code—no TODOs or ellipses.
4) End your message with the Verification Checklist (see §14).
````

---

## 4) Golden rules for Copilot

* Make **small, testable** diffs.
* **Never invent** DocTypes/fields/links; **back-trace** first (see §9).
* Prefer **Frappe APIs**/Query Builder to raw SQL.
* All new/changed `.py` and `.js` must have the **mandatory header** (see §5).
* Every DocType must ship with a **README.md** (see §8.2).
* All server mutations: **validate** fields, permissions, workflow state; **log** key actions.
* Keep UI in `.js/.vue`, business rules in `.py`, schema in `.json`, docs in `README.md`.
* Tests for every controller/validator/workflow path (see §10).

---

## 5) Mandatory file header (all `.py` and `.js`)

Place this at line 1 of **every** Python/JavaScript file and keep it updated:

```text
# Path: <repo-relative path, e.g., repair_portal/repair_portal/doctype/invoice/invoice.py>
# Date: <YYYY-MM-DD>            # ISO-8601; update when behavior changes
# Version: <MAJOR.MINOR.PATCH>  # semver; bump on behavior change
# Description: <1–3 lines: purpose, responsibilities, side effects>
# Dependencies: <imports/services this file relies on; optional>
```

> Copilot enforcement prompt: *“When creating or editing any `.py` or `.js`, insert or update the 5-line header (Path/Date/Version/Description/Dependencies).”*

---

## 6) Repository & naming conventions

* **Apps:** `repair_portal/repair_portal/...`
* **DocTypes:** `repair_portal/repair_portal/doctype/<doctype_name>/`

  * Files: `<doctype_name>.json`, `<doctype_name>.py`, `<doctype_name>.js`, `README.md`, `tests/test_<doctype_name>.py`
* **Names:** modules & fieldnames = `snake_case`; DocType labels = Title Case.
* **Branches:** `feat/*`, `fix/*`, `docs/*`, `chore/*`, `ops/*`.
* **Commits:** Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:` …).
* **Versioning:** Semantic Versioning (MAJOR.MINOR.PATCH). Update `CHANGELOG.md`.

---

## 7) Coding standards

| Layer               | Must-use patterns                                                                                             |
| ------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Python**          | PEP8 • type hints where practical • `frappe.get_doc/new_doc` • Query Builder • no `db.commit()` in requests   |
| **JavaScript**      | `frappe.ui.form.on` for form events • no inline HTML • handle failures • translate strings with `__()`        |
| **Vue/React**       | Prefer `.vue` for portal UI in `repair_portal/public/js/` • Tailwind + shadcn/ui • ARIA: keyboard-navigable   |
| **DocTypes (JSON)** | `workflow_state` is **Select** (not Link) when used • avoid deprecated keys • aim for explicit `description`s |
| **HTML/Jinja**      | Jinja where necessary; escape/whitelist inputs                                                                |

**Python controller skeleton (server):**

```python
# Path: repair_portal/repair_portal/doctype/invoice/invoice.py
# Date: 2025-08-15
# Version: 1.0.0
# Description: Server controller for Invoice; naming, validation, workflow guards.
# Dependencies: frappe, frappe.model.naming

import frappe
from frappe import _
from frappe.model.document import Document

class Invoice(Document):
    def before_insert(self):
        self._enforce_naming_series()
        self._assert_required()

    def validate(self):
        self._validate_links()
        self._business_rules()

    def on_submit(self):
        self._sync_linked_docs()

    # helpers
    def _enforce_naming_series(self):
        if not self.naming_series:
            self.naming_series = "INV-.YYYY.-"

    def _assert_required(self):
        required = ["customer", "posting_date", "currency"]
        missing = [f for f in required if not self.get(f)]
        if missing:
            frappe.throw(_("Missing required: {0}").format(", ".join(missing)))

    def _validate_links(self):
        # add cross-doc semantic checks as needed
        pass

    def _business_rules(self):
        pass

    def _sync_linked_docs(self):
        pass
```

**Client script skeleton:**

```javascript
// Path: repair_portal/repair_portal/doctype/invoice/invoice.js
// Date: 2025-08-15
// Version: 1.0.0
// Description: Form events, UI validations, link filters.
// Dependencies: frappe

frappe.ui.form.on('Invoice', {
  onload(frm) {
    frm.set_query('customer', () => ({ filters: { disabled: 0 } }));
  },
  refresh(frm) {
    // UI-only logic
  }
});
```

---

## 8) DocType standards

### 8.1 Required assets per DocType

* `<doctype>.json` (schema & perms)
* `<doctype>.py` (server controller)
* `<doctype>.js` (client/UI logic)
* `README.md` (**mandatory explainer**)
* `tests/test_<doctype>.py` (unit/integration tests)

### 8.2 `README.md` template (place beside the DocType)

```md
# <DocType Label> (`<doctype_name>`)

## Purpose
What this DocType represents and why it exists.

## Schema Summary
- **Naming:** `naming_series` = …
- **Key Fields:** business-critical fields + purpose.
- **Links:**
  - `<link_field>` → `<Target DocType>` (cardinality & rationale)
- **Child Tables:**
  - `<table_field>` → `<Child DocType>` (row meaning & constraints)

## Business Rules
Validation hooks (`validate`, `before_insert`, `on_submit`, …), derived fields, side-effects.

## Workflows
States, transitions, actions/roles, docstatus mapping; linked docs produced/consumed.

## Client Logic (`<doctype>.js`)
Handlers, query filters, UI guards.

## Server Logic (`<doctype>.py`)
Public/whitelisted methods, parameters, permission gates, background jobs.

## Data Integrity
Required fields, defaults, de-duplication, referential integrity notes.

## Test Plan
Scenarios, fixtures, coverage expectations.

## Changelog
- YYYY-MM-DD – change note
```

### 8.3 Descriptions & duplication

* Add `description` for any confusing DocType/field/child table.
* Avoid duplicate or near-duplicate fields. If scopes overlap, **merge** into a canonical field and deprecate the other with a data patch (see §11.4).

### 8.4 Links & child tables (back-trace rules)

For each `Link`/`Table` field:

1. Target DocType **exists** (in repo or installed app).
2. Link rationale documented in the DocType README.
3. Define delete behavior (deny/cascade/custom clean-up) in controller if needed.
4. Tests assert referential integrity and query filters.
5. JS sets `frm.set_query` filters consistent with server checks.

### 8.5 Workflows

* Provide a `workflow_state` Select field when using Workflows.
* List all **states** and **transitions** (action, role, condition, next\_state).
* Map to docstatus intentionally (0/1/2).
* Keep **linked docs** in sync (e.g., SO→DN→SI states/actions).
* Tests must cover valid/invalid transitions.

---

## 9) Controller back-trace checklist (for creators/updaters)

When a controller creates/updates other docs, ensure:

* [ ] **All required fields** present on new docs (`doc.get_missing_mandatory_fields()` or manual checks).
* [ ] **Naming** follows conventions (`naming_series`, or explicit autoname with `make_autoname`).
* [ ] **Permissions** enforced (`frappe.has_permission` and doc perms).
* [ ] **Workflow guards** enforced before transitions/submit/cancel.
* [ ] **Links** resolve to existing docs; reject if missing/invalid.
* [ ] **Idempotency** for retry (use natural keys or unique constraints where appropriate).
* [ ] **Transactions** rely on Frappe; no manual `db.commit()` in requests.
* [ ] **Logs** for critical actions (`frappe.logger` / `frappe.log_error`).
* [ ] **Tests** for happy paths + failure cases.

---

## 10) Testing & quality gates

### 10.1 Unit/integration tests

Location: `repair_portal/repair_portal/doctype/<doctype>/tests/test_<doctype>.py`
Cover: required fields, link integrity, workflow transitions (valid+invalid), and side effects.
Target **≥80%** module coverage.

Example:

```python
import frappe, pytest

def test_invoice_requires_fields():
    doc = frappe.get_doc({"doctype": "Invoice"})
    with pytest.raises(frappe.ValidationError):
        doc.insert()

def test_workflow_happy_path():
    # build fixtures; create → submit; assert states/docstatus
    pass
```

### 10.2 Static analysis & style

* **Python:** Black, Ruff, isort, Bandit
* **JS:** ESLint, Prettier
* **JSON:** validate DocType format (schema & links)
* **Build:** `bench build` for portal assets

---

## 11) Data model hygiene & migrations

### 11.1 De-duplicate & merge

Before adding fields, search for similar scope (≥70% overlap). If merging:

* Add a **reentrant patch** to backfill data.
* Mark old field hidden/readonly for one release; remove next **MAJOR**.
* Update controllers, client scripts, tests, and README.

### 11.2 Referential integrity

* Link/Table `options` must point to an existing DocType.
* Child rows: ensure `parenttype`/`parentfield` are correct.
* Decide parent deletion policy and enforce in code.

### 11.3 Fixtures & seeds

* Provide minimal, idempotent fixtures for smoke tests.

### 11.4 Patches

* Place in `repair_portal/repair_portal/patches/<module>/YYYYMMDD_slug.py`.
* Reentrant; log progress; document in DocType README → *Changelog*.

---

## 12) Domain-specific automations (clarinet workflow)

| Trigger                         | Automation                                                                            |
| ------------------------------- | ------------------------------------------------------------------------------------- |
| **Clarinet Intake** (Inventory) | Create **Serial No**, **Initial Intake Inspection**, **Clarinet Initial Setup** docs. |
| **JS & PY Controllers**         | Use controllers for conditional fields & all automations; client side is UI-only.     |
| **Technician Portal**           | Must be keyboard-navigable; include ARIA labels; no mouse-only actions.               |

> For each automation, write the DocType README sections (*Business Rules*, *Server Logic*, *Workflows*) and add tests asserting the created docs & states.

---

## 13) PR checklist (developer & reviewer)

* [ ] **Headers** present/updated in all changed `.py`/`.js`.
* [ ] Every touched DocType has an updated **README.md**.
* [ ] All Link/Table targets exist; validator passes.
* [ ] No duplicate/near-duplicate fields; patches included for merges.
* [ ] Controllers enforce required fields, naming, permissions, and workflow guards.
* [ ] Workflows aligned across linked docs; transitions tested.
* [ ] Linting, type checks, and tests pass in CI.
* [ ] Security review: PII, permissions, secrets, logs.
* [ ] Docs & `CHANGELOG.md` updated.

---

## 14) Verification checklist (local)

```bash
# Pull latest & migrate
bench --site erp.artisanclarinets.com migrate

# Build assets
bench build

# Run targeted tests
bench --site erp.artisanclarinets.com run-tests --module repair_portal.tests.<module>

# Full suite (optional)
bench --site erp.artisanclarinets.com run-tests --app repair_portal
```

---

## 15) Automation scripts & CI```

### 15.1 `scripts/enforce_headers.py`

```bash
#!/usr/bin/env python3
# Path: scripts/enforce_headers.py
# Date: 2025-08-15
# Version: 1.0.0
# Description: Ensures required header on .py/.js files; inserts default if missing.
# Dependencies: python stdlib (re, datetime, pathlib), invoked via pre-commit

import sys, pathlib, datetime, re

HEADER_RX = re.compile(
    r"(?s)\A# Path: .+\n# Date: \d{4}-\d{2}-\d{2}\n# Version: \d+\.\d+\.\d+\n# Description: .+\n(?:# Dependencies: .*\n)?"
)

def ensure_header(p: pathlib.Path):
    text = p.read_text(encoding="utf-8")
    if not HEADER_RX.match(text):
        rel = p.as_posix()
        today = datetime.date.today().isoformat()
        header = (
            f"# Path: {rel}\n"
            f"# Date: {today}\n"
            f"# Version: 0.1.0\n"
            f"# Description: <fill in summary>\n"
            f"# Dependencies: <imports/services>\n\n"
        )
        p.write_text(header + text, encoding="utf-8")
        return True
    return False

if __name__ == "__main__":
    changed = 0
    for arg in sys.argv[1:]:
        p = pathlib.Path(arg)
        if p.suffix in (".py", ".js") and p.exists():
            changed += int(ensure_header(p))
    print(f"Headers enforced on {changed} files.")
```

### 15.2 `scripts/validate_doctypes.py` (offline JSON checks)

```python
#!/usr/bin/env python3
# Path: scripts/validate_doctypes.py
# Date: 2025-08-15
# Version: 1.1.0
# Description: Static validation for DocType JSONs: broken links, child tables, dup fields, missing descriptions.
# Dependencies: python stdlib (json, pathlib)

import json, pathlib, sys

ROOT = pathlib.Path("repair_portal/repair_portal/doctype")
errors, warnings = [], []

def load_doctypes():
    for json_path in ROOT.glob("*/**/*.json"):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            yield json_path, data
        except Exception as e:
            errors.append((json_path, f"Invalid JSON: {e}"))

# pass 1: collect names
doctypes = set()
for path, data in load_doctypes():
    name = data.get("name") or data.get("doctype")
    if name: doctypes.add(name)

# pass 2: validate
for path, data in load_doctypes():
    fields = data.get("fields", [])
    seen = set()
    for f in fields:
        fname, ftype = f.get("fieldname"), f.get("fieldtype")
        if not fname:
            errors.append((path, "Field without fieldname"))
            continue
        if fname in seen:
            errors.append((path, f"Duplicate fieldname: {fname}"))
        seen.add(fname)

        if ftype == "Link":
            target = f.get("options")
            if not target:
                errors.append((path, f"Link field {fname} missing options (target DocType)"))
            elif target not in doctypes:
                errors.append((path, f"Broken Link target '{target}' in {fname}"))
            if not f.get("description"):
                warnings.append((path, f"Missing description for Link {fname}"))

        if ftype == "Table":
            child = f.get("options")
            if not child or child not in doctypes:
                errors.append((path, f"Broken Child Table target '{child}' in {fname}"))
            if not f.get("description"):
                warnings.append((path, f"Missing description for Table {fname}"))

        if ftype in {"Dynamic Link","Code"} and not f.get("description"):
            warnings.append((path, f"Add description for {ftype} field {fname}"))

    # workflow_state presence advisory
    if any(f.get("fieldname") == "workflow_state" for f in fields):
        pass

for p, msg in errors + warnings:
    stream = sys.stderr if (p, msg) in errors else sys.stdout
    print(f"[{p}] {msg}", file=stream)

sys.exit(1 if errors else 0)
```
---

## 16) Security, privacy, logging

* No credentials/PII in code or logs; use `site_config.json` for secrets.
* Enforce permissions server-side; default-deny mindset.
* Log critical transitions and cross-doc creations (who/when/what) via `frappe.logger()` or dedicated Audit Log DocType.
* Validate/escape user inputs; rate-limit whitelisted methods when appropriate.

---

## 17) Performance & resilience

* Keep requests light; offload heavy work to `frappe.enqueue`.
* Index frequently filtered fields (DocType or patch).
* Cache readonly config with `frappe.cache()`; invalidate on change.
* Keep portal API responses ≤200 ms P50 where feasible; paginate list endpoints.

---

## 18) Internationalization & accessibility

* Wrap UI strings in `__()`.
* Use descriptive `label`/`description` for screen readers.
* Keyboard-navigable portal (ARIA on interactive controls).
* Store UTC on server; show per site timezone.

---

## 19) Governance & docs

* Maintain `CHANGELOG.md`.
* Add `CODEOWNERS` for DocType paths.
* PR template must prompt for headers/README/tests/migrations/workflows re-verifications.
* Keep ADRs under `docs/adr/000X-title.md` for architectural decisions.

---

## 20) Coding aids (drop-in Copilot prompts)

**Create a new DocType with docs & tests**

> Generate `<doctype>.json`, `<doctype>.py`, `<doctype>.js`, and `README.md` as per COPILOT\_INSTRUCTIONS.md §8. Include required fields A/B/C; link to `<Target DocType>` with `frm.set_query` filters; add tests for required fields + one valid workflow transition.

**Add a safe mutation endpoint**

> Create a whitelisted method `repair_portal.api.update_foo(args)` that validates permissions, required fields, and workflow guards; updates/creates linked docs idempotently; logs actions; adds tests for success/failure.

**Refactor duplicate fields**

> This is in a development site, so no data is at risk of being corrupted. Please proceed with the refactoring.

---

## 21) Compliance checklist (Frappe v15)

* `workflow_state` **Select**, never Link.
* No deprecated keys (e.g., `__onload` in JSON).
* No orphaned DocTypes or circular imports.
* Tests pass via `bench --site erp.artisanclarinets.com run-tests`.
* For JSON, Frappe uses InnoDB by default—engine override not required unless you know why.

---

## 22) Portal/UI specifics

* Prefer `.vue` components in `repair_portal/public/js/`.
* Tailwind + shadcn/ui; avoid custom CSS unless necessary.
* No inline HTML in JS; components/templates only.
* Always handle async failures and show accessible toasts/messages.

---

## 23) Example minimal DocType JSON stub

```json
{
  "doctype": "DocType",
  "name": "Invoice",
  "module": "Billing",
  "naming_rule": "Naming Series",
  "autoname": "naming_series:",
  "fields": [
    {"fieldname":"naming_series","fieldtype":"Select","label":"Naming Series","options":"INV-.YYYY.-","reqd":1,"description":"Series for autoname"},
    {"fieldname":"customer","fieldtype":"Link","options":"Customer","label":"Customer","reqd":1,"in_list_view":1,"description":"Customer to bill"},
    {"fieldname":"items","fieldtype":"Table","options":"Invoice Item","label":"Items","reqd":1,"description":"Line items to invoice"},
    {"fieldname":"workflow_state","fieldtype":"Select","label":"Workflow State","options":"Draft\nSubmitted\nCancelled","read_only":1}
  ],
  "permissions": [
    {"role":"System Manager","read":1,"write":1,"create":1,"submit":1,"cancel":1,"delete":1}
  ],
  "track_changes": 1
}
```

---

## 24) What to do when something is confusing

* Add/expand `description` on fields/DocTypes.
* Add **Examples** to the DocType README.
* If still ambiguous, add an **ADR** capturing the chosen approach and rationale.

---

### Appendix A — Domain note: Clarinet Intake automation

* When **Clarinet Intake** is created: programmatically create **Instrument Serial No**, **Instrument Inspection**, and **Clarinet Initial Setup**.
* Controllers must validate required fields, ensure naming conventions, link targets exist, and write audit logs.
* Tests must assert each created doc exists with the expected workflow state.

---

### Appendix B — Quick navigation (repo paths)

* Module → `repair_portal/repair_portal/<module>/`
* DocType → `repair_portal/repair_portal/<module>/doctype/<doctype_name>/<doctype_name>.json`
* Tests → `repair_portal/repair_portal/<module>/doctype/<doctype_name>/test_<doctype_name>.py`
* Scripts → `scripts/*.py`

---

**Adopt this file at the repo root as `COPILOT_INSTRUCTIONS.md`.**
Copilot should treat it as the single source of truth for headers, DocType documentation, link integrity, controller back-tracing, migrations, workflows, tests, security, and CI.available tools, focus areas, and any mode-specific instructions or constraints.