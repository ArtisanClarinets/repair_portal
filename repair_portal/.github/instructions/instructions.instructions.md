---
applyTo: '**'
---
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

```python
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
Copilot should treat it as the single source of truth for headers, DocType documentation, link integrity, controller back-tracing, migrations, workflows, tests, security, and CI.

### Appendix C — App File Structure

      repair_portal
        ├── AGENTS.md
        ├── biome.json
        ├── CHANGELOG.md
        ├── controller_review.md
        ├── cypress.config.js
        ├── documentation
        │   ├── DASHBOARD_CHARTS.md
        │   ├── DOCTYPE.md
        │   ├── REPORT.md
        │   ├── WORKFLOW.md
        │   └── WORKSPACE.md
        ├── eslint.config.js
        ├── license.txt
        ├── modules.txt
        ├── package.json
        ├── pyproject.toml
        ├── README.md
        ├── repair_portal
        │   ├── api
        │   │   ├── clarinet_utils.py
        │   │   ├── client_portal.py
        │   │   ├── customer.py
        │   │   ├── frontend
        │   │   │   ├── customer_profile.py
        │   │   │   ├── __init__.py
        │   │   │   ├── instrument_profile.py
        │   │   │   └── player_profile.py
        │   │   ├── __init__.py
        │   │   ├── intake_dashboard.py
        │   │   └── technician_dashboard.py
        │   ├── config
        │   │   ├── desktop.py
        │   │   └── __init__.py
        │   ├── customer
        │   │   ├── CHANGELOG.md
        │   │   ├── dashboard
        │   │   │   └── client_dashboard
        │   │   │       ├── client_dashboard.json
        │   │   │       └── client_dashboard.py
        │   │   ├── doctype
        │   │   │   ├── consent_field_value
        │   │   │   │   ├── consent_field_value.js
        │   │   │   │   ├── consent_field_value.json
        │   │   │   │   ├── consent_field_value.py
        │   │   │   │   └── __init__.py
        │   │   │   ├── consent_form
        │   │   │   │   ├── consent_form.js
        │   │   │   │   ├── consent_form.json
        │   │   │   │   ├── consent_form.py
        │   │   │   │   └── __init__.py
        │   │   │   ├── consent_log
        │   │   │   │   ├── consent_log.json
        │   │   │   │   └── consent_log.py
        │   │   │   ├── consent_log_entry
        │   │   │   │   ├── consent_log_entry.json
        │   │   │   │   └── consent_log_entry.py
        │   │   │   ├── consent_required_field
        │   │   │   │   ├── consent_required_field.js
        │   │   │   │   ├── consent_required_field.json
        │   │   │   │   ├── consent_required_field.py
        │   │   │   │   └── __init__.py
        │   │   │   ├── consent_template
        │   │   │   │   ├── consent_template.js
        │   │   │   │   ├── consent_template.json
        │   │   │   │   ├── consent_template.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── test_consent_template.py
        │   │   │   ├── customer_consent
        │   │   │   │   ├── customer_consent_form.py
        │   │   │   │   ├── customer_consent.js
        │   │   │   │   ├── customer_consent.json
        │   │   │   │   ├── customer_consent.py
        │   │   │   │   └── __init__.py
        │   │   │   ├── customer_type
        │   │   │   │   ├── customer_type.json
        │   │   │   │   ├── customer_type.py
        │   │   │   │   └── __init__.py
        │   │   │   ├── __init__.py
        │   │   │   ├── instruments_owned
        │   │   │   │   ├── instruments_owned.json
        │   │   │   │   └── instruments_owned.py
        │   │   │   └── linked_players
        │   │   │       ├── __init__.py
        │   │   │       ├── linked_players.js
        │   │   │       ├── linked_players.json
        │   │   │       └── linked_players.py
        │   │   ├── events
        │   │   │   └── utils.py
        │   │   ├── __init__.py
        │   │   ├── module_health.md
        │   │   ├── notification
        │   │   │   └── draft_customer
        │   │   │       └── draft_customer.json
        │   │   ├── technical_debt.md
        │   │   ├── workflow
        │   │   │   └── customer_workflow
        │   │   │       └── customer_workflow.json
        │   │   ├── workflow_action_master
        │   │   │   └── customer_setup_actions
        │   │   │       ├── customer_setup_actions.json
        │   │   │       └── customer_setup_actions.py
        │   │   └── workflow_state
        │   │       ├── active
        │   │       │   └── active.json
        │   │       ├── archived
        │   │       │   └── archived.json
        │   │       ├── deleted
        │   │       │   └── deleted.json
        │   │       ├── draft
        │   │       │   └── draft.json
        │   │       └── workflow_state.py
        │   ├── docs
        │   │   ├── customer_autocreate_setup.md
        │   │   ├── Frappe-v15-file-guide.json
        │   │   ├── JS_API.MD
        │   │   ├── new_instrument_intake.md
        │   │   ├── PYTHON_API.md
        │   │   └── READMEs.md
        │   ├── doctype_audit.py
        │   ├── enhancements
        │   │   ├── config
        │   │   │   └── desktop.py
        │   │   ├── dashboard_chart
        │   │   │   └── upgrade_requests_over_time
        │   │   │       └── upgrade_requests_over_time.json
        │   │   ├── doctype
        │   │   │   ├── customer_upgrade_request
        │   │   │   │   ├── customer_upgrade_request.json
        │   │   │   │   └── customer_upgrade_request.py
        │   │   │   └── upgrade_option
        │   │   │       ├── upgrade_option.json
        │   │   │       └── upgrade_option.py
        │   │   ├── __init__.py
        │   │   └── report
        │   │       ├── top_upgrade_requests
        │   │       │   ├── top_upgrade_requests.json
        │   │       │   └── top_upgrade_requests.py
        │   │       └── upgrade_conversion_rates
        │   │           ├── upgrade_conversion_rates.json
        │   │           └── upgrade_conversion_rates.py
        │   ├── hooks.py
        │   ├── __init__.py
        │   ├── inspection
        │   │   ├── config
        │   │   │   ├── desktop.py
        │   │   │   ├── docs.py
        │   │   │   └── __init__.py
        │   │   ├── doctype
        │   │   │   ├── __init__.py
        │   │   │   └── instrument_inspection
        │   │   │       ├── current_instrument_inspection
        │   │   │       ├── __init__.py
        │   │   │       ├── instrument_inspection.js
        │   │   │       ├── instrument_inspection.json
        │   │   │       ├── instrument_inspection.py
        │   │   │       ├── README.md
        │   │   │       └── test_instrument_inspection.py
        │   │   ├── __init__.py
        │   │   ├── migrate_clarinet_inspection_to_report.py
        │   │   ├── modules.txt
        │   │   ├── page
        │   │   │   ├── __init__.py
        │   │   │   └── technician_dashboard
        │   │   │       ├── __init__.py
        │   │   │       ├── technician_dashboard.js
        │   │   │       └── technician_dashboard.json
        │   │   ├── README.md
        │   │   └── workflow
        │   │       └── inspection_report_workflow.json
        │   ├── install.py
        │   ├── instrument_profile
        │   │   ├── config
        │   │   │   ├── desktop.py
        │   │   │   └── __init__.py
        │   │   ├── cron
        │   │   │   └── warranty_expiry_check.py
        │   │   ├── dashboard_chart
        │   │   │   ├── instrument_status_distribution
        │   │   │   │   └── instrument_status_distribution.json
        │   │   │   └── warranty_distribution
        │   │   │       └── warranty_distribution.json
        │   │   ├── doctype
        │   │   │   ├── client_instrument_profile
        │   │   │   │   ├── client_instrument_profile.js
        │   │   │   │   ├── client_instrument_profile.json
        │   │   │   │   ├── client_instrument_profile.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── test_client_instrument_profile.py
        │   │   │   ├── customer_external_work_log
        │   │   │   │   ├── customer_external_work_log.js
        │   │   │   │   ├── customer_external_work_log.json
        │   │   │   │   ├── customer_external_work_log.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── test_customer_external_work_log.py
        │   │   │   ├── __init__.py
        │   │   │   ├── instrument
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── instrument.js
        │   │   │   │   ├── instrument.json
        │   │   │   │   ├── instrument.py
        │   │   │   │   └── README.md
        │   │   │   ├── instrument_accessory
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── instrument_accessory.json
        │   │   │   │   ├── instrument_accessory.py
        │   │   │   │   └── README.md
        │   │   │   ├── instrument_category
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── instrument_category.js
        │   │   │   │   ├── instrument_category.json
        │   │   │   │   ├── instrument_category.py
        │   │   │   │   └── test_instrument_category.py
        │   │   │   ├── instrument_condition_record
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── instrument_condition_record.json
        │   │   │   │   ├── instrument_condition_record.py
        │   │   │   │   └── test_instrument_condition_record.py
        │   │   │   ├── instrument_model
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── instrument_model.js
        │   │   │   │   ├── instrument_model.json
        │   │   │   │   ├── instrument_model.py
        │   │   │   │   └── test_instrument_model.py
        │   │   │   ├── instrument_photo
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── instrument_photo.json
        │   │   │   │   ├── instrument_photo.py
        │   │   │   │   └── README.md
        │   │   │   ├── instrument_profile
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── instrument_profile.js
        │   │   │   │   ├── instrument_profile.json
        │   │   │   │   ├── instrument_profile_list.js
        │   │   │   │   ├── instrument_profile.py
        │   │   │   │   ├── README.md
        │   │   │   │   └── test_instrument_profile.py
        │   │   │   └── instrument_serial_number
        │   │   │       ├── __init__.py
        │   │   │       ├── instrument_serial_number.js
        │   │   │       ├── instrument_serial_number.json
        │   │   │       ├── instrument_serial_number.py
        │   │   │       └── test_instrument_serial_number.py
        │   │   ├── events
        │   │   │   ├── __init__.py
        │   │   │   └── utils.py
        │   │   ├── __init__.py
        │   │   ├── module_def
        │   │   │   └── instrument_profile.json
        │   │   ├── notification
        │   │   │   ├── instrument_status_change
        │   │   │   │   └── instrument_status_change.json
        │   │   │   ├── missing_customer
        │   │   │   │   └── missing_customer.json
        │   │   │   └── missing_player_profile
        │   │   │       └── missing_player_profile.json
        │   │   ├── print_format
        │   │   │   ├── instrument_qr_tag
        │   │   │   │   └── instrument_qr_tag.json
        │   │   │   ├── instrument_summary
        │   │   │   │   └── instrument_summary.json
        │   │   │   └── instrument_tag
        │   │   │       └── instrument_tag.json
        │   │   ├── report
        │   │   │   ├── instrument_inventory_report
        │   │   │   │   ├── instrument_inventory_report.json
        │   │   │   │   └── instrument_inventory_report.py
        │   │   │   ├── instrument_profile_report
        │   │   │   │   ├── instrument_profile_report.json
        │   │   │   │   └── instrument_profile_report.py
        │   │   │   ├── instrument_service_history
        │   │   │   │   ├── instrument_service_history.json
        │   │   │   │   └── instrument_service_history.py
        │   │   │   ├── pending_client_instruments
        │   │   │   │   ├── pending_client_instruments.json
        │   │   │   │   └── pending_client_instruments.py
        │   │   │   └── warranty_status_report
        │   │   │       ├── warranty_status_report.json
        │   │   │       └── warranty_status_report.py
        │   │   ├── services
        │   │   │   └── profile_sync.py
        │   │   ├── web_form
        │   │   │   ├── client_instrument_profile
        │   │   │   │   └── client_instrument_profile.json
        │   │   │   ├── __init__.py
        │   │   │   ├── instrument_intake_batch
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── instrument_intake_batch.js
        │   │   │   │   ├── instrument_intake_batch.json
        │   │   │   │   └── instrument_intake_batch.py
        │   │   │   └── instrument_registration
        │   │   │       ├── __init__.py
        │   │   │       ├── instrument_registration.js
        │   │   │       ├── instrument_registration.json
        │   │   │       └── instrument_registration.py
        │   │   ├── workflow
        │   │   │   └── instrument_profile_workflow
        │   │   │       └── instrument_profile_workflow.json
        │   │   └── workflow_state
        │   │       ├── archived
        │   │       │   └── archived.json
        │   │       ├── closed
        │   │       │   └── closed.json
        │   │       ├── delivered
        │   │       │   └── delivered.json
        │   │       ├── draft
        │   │       │   └── draft.json
        │   │       ├── in_progress
        │   │       │   └── in_progress.json
        │   │       ├── open
        │   │       │   └── open.json
        │   │       ├── ready_for_use
        │   │       │   └── ready_for_use.json
        │   │       ├── resolved
        │   │       │   └── resolved.json
        │   │       ├── waiting_on_client
        │   │       │   └── waiting_on_client.json
        │   │       └── waiting_on_player
        │   │           └── waiting_on_player.json
        │   ├── instrument_setup
        │   │   ├── config
        │   │   │   └── desktop.py
        │   │   ├── data
        │   │   │   ├── clarinet_pad_map_bundled.json
        │   │   │   ├── clarinet_setup_operation_bundled.json
        │   │   │   ├── instrument_model_bundled.json
        │   │   │   ├── setup_checklist_item_bundled.json
        │   │   │   └── setup_template_bundled.json
        │   │   ├── doctype
        │   │   │   ├── clarinet_initial_setup
        │   │   │   │   ├── clarinet_initial_setup.js
        │   │   │   │   ├── clarinet_initial_setup.json
        │   │   │   │   ├── clarinet_initial_setup.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── README.md
        │   │   │   │   ├── README.md.backup
        │   │   │   │   └── test_clarinet_initial_setup.py
        │   │   │   ├── clarinet_pad_entry
        │   │   │   │   ├── clarinet_pad_entry.json
        │   │   │   │   ├── clarinet_pad_entry.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── README.md
        │   │   │   ├── clarinet_pad_map
        │   │   │   │   ├── clarinet_pad_map.js
        │   │   │   │   ├── clarinet_pad_map.json
        │   │   │   │   ├── clarinet_pad_map.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── README.md
        │   │   │   │   └── test_clarinet_pad_map.py
        │   │   │   ├── clarinet_setup_log
        │   │   │   │   ├── clarinet_setup_log.js
        │   │   │   │   ├── clarinet_setup_log.json
        │   │   │   │   ├── clarinet_setup_log.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── README.md
        │   │   │   │   └── test_clarinet_setup_log.py
        │   │   │   ├── clarinet_setup_operation
        │   │   │   │   ├── clarinet_setup_operation.json
        │   │   │   │   ├── clarinet_setup_operation.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── README.md
        │   │   │   ├── clarinet_setup_task
        │   │   │   │   ├── clarinet_setup_task.js
        │   │   │   │   ├── clarinet_setup_task.json
        │   │   │   │   ├── clarinet_setup_task_list.js
        │   │   │   │   ├── clarinet_setup_task.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── README.md
        │   │   │   │   └── test_clarinet_setup_task.py
        │   │   │   ├── clarinet_task_depends_on
        │   │   │   │   ├── clarinet_task_depends_on.js
        │   │   │   │   ├── clarinet_task_depends_on.json
        │   │   │   │   ├── clarinet_task_depends_on.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── README.md
        │   │   │   │   └── test_clarinet_task_depends_on.py
        │   │   │   ├── clarinet_template_task
        │   │   │   │   ├── clarinet_template_task.js
        │   │   │   │   ├── clarinet_template_task.json
        │   │   │   │   ├── clarinet_template_task.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── README.md
        │   │   │   │   └── test_clarinet_template_task.py
        │   │   │   ├── clarinet_template_task_depends_on
        │   │   │   │   ├── clarinet_template_task_depends_on.json
        │   │   │   │   ├── clarinet_template_task_depends_on.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── README.md
        │   │   │   ├── __init__.py
        │   │   │   ├── setup_checklist_item
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── README.md
        │   │   │   │   ├── setup_checklist_item.json
        │   │   │   │   └── setup_checklist_item.py
        │   │   │   ├── setup_material_log
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── README.md
        │   │   │   │   ├── setup_material_log.js
        │   │   │   │   ├── setup_material_log.json
        │   │   │   │   ├── setup_material_log.py
        │   │   │   │   └── test_setup_material_log.py
        │   │   │   └── setup_template
        │   │   │       ├── __init__.py
        │   │   │       ├── README.md
        │   │   │       ├── setup_template.js
        │   │   │       ├── setup_template.json
        │   │   │       ├── setup_template.py
        │   │   │       └── test_setup_template.py
        │   │   ├── hooks
        │   │   │   ├── after_install
        │   │   │   │   ├── create_a_clarinet_standard_template.py
        │   │   │   │   ├── create_bb_clarinet_standard_template.py
        │   │   │   │   └── create_eb_clarinet_standard_template.py
        │   │   │   ├── load_templates.py
        │   │   │   └── templates
        │   │   │       ├── brand_bundled.json
        │   │   │       ├── create_a_clarinet_standard_template.json
        │   │   │       ├── create_bb_clarinet_standard_template.json
        │   │   │       └── instrument_model_import.json
        │   │   ├── __init__.py
        │   │   ├── print_format
        │   │   │   ├── clarinet_setup_certificate
        │   │   │   │   ├── clarinet_setup_certificate.html
        │   │   │   │   ├── clarinet_setup_certificate.json
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── README.md
        │   │   │   └── __init__.py
        │   │   ├── README.md
        │   │   ├── report
        │   │   │   ├── parts_consumption
        │   │   │   │   ├── parts_consumption.json
        │   │   │   │   └── parts_consumption.py
        │   │   │   ├── technician_performance
        │   │   │   │   ├── technician_performance.json
        │   │   │   │   └── technician_performance.py
        │   │   │   └── turnaround_time_analysis
        │   │   │       ├── turnaround_time_analysis.json
        │   │   │       └── turnaround_time_analysis.sql
        │   │   └── web_form
        │   │       └── repair_status
        │   │           └── repair_status.json
        │   ├── intake
        │   │   ├── config
        │   │   │   └── desktop.py
        │   │   ├── doctype
        │   │   │   ├── brand_mapping_rule
        │   │   │   │   ├── brand_mapping_rule.json
        │   │   │   │   ├── brand_mapping_rule.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── README.md
        │   │   │   ├── clarinet_intake
        │   │   │   │   ├── clarinet_intake.js
        │   │   │   │   ├── clarinet_intake.json
        │   │   │   │   ├── clarinet_intake.py
        │   │   │   │   ├── clarinet_intake_timeline.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── README.md
        │   │   │   │   └── test_clarinet_intake.py
        │   │   │   ├── clarinet_intake_settings
        │   │   │   │   ├── clarinet_intake_settings.json
        │   │   │   │   ├── clarinet_intake_settings.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── README.md
        │   │   │   ├── __init__.py
        │   │   │   ├── intake_accessory_item
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── intake_accessory_item.json
        │   │   │   │   ├── intake_accessory_item.py
        │   │   │   │   └── README.md
        │   │   │   ├── loaner_instrument
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── loaner_instrument.json
        │   │   │   │   ├── loaner_instrument.py
        │   │   │   │   └── README.md
        │   │   │   └── loaner_return_check
        │   │   │       ├── __init__.py
        │   │   │       ├── loaner_return_check.json
        │   │   │       ├── loaner_return_check.py
        │   │   │       └── README.md
        │   │   ├── hooks
        │   │   │   └── load_templates.py
        │   │   ├── __init__.py
        │   │   ├── print_format
        │   │   │   └── intake_receipt.json
        │   │   ├── README.md
        │   │   ├── services
        │   │   │   └── intake_sync.py
        │   │   ├── templates
        │   │   │   └── loaner_agreement_template.html
        │   │   ├── test
        │   │   │   └── test_clarinet_intake.py
        │   │   ├── utils
        │   │   │   └── emailer.py
        │   │   ├── web_form
        │   │   │   └── clarinet_intake_request
        │   │   │       └── clarinet_intake_request.json
        │   │   ├── workflow
        │   │   │   ├── intake_workflow
        │   │   │   │   └── intake_workflow.json
        │   │   │   └── loaner_return_check_workflow
        │   │   │       └── loaner_return_check_workflow.json
        │   │   ├── workflow_action_master
        │   │   │   ├── begin_inspection
        │   │   │   │   └── begin_inspection.json
        │   │   │   ├── customer_approval
        │   │   │   │   └── customer_approval.json
        │   │   │   ├── customer_rejection
        │   │   │   │   └── customer_rejection.json
        │   │   │   ├── logged_received
        │   │   │   │   └── logged_received.json
        │   │   │   ├── proceed_to_setup
        │   │   │   │   └── proceed_to_setup.json
        │   │   │   ├── repair_complete
        │   │   │   │   └── repair_complete.json
        │   │   │   ├── send_estimate_approval
        │   │   │   │   └── send_estimate_approval.json
        │   │   │   └── setup_complete
        │   │   │       └── setup_complete.json
        │   │   └── workflow_state
        │   │       ├── awaiting_customer_approval
        │   │       │   └── awaiting_customer_approval.json
        │   │       ├── awaiting_payment
        │   │       │   └── awaiting_payment.json
        │   │       ├── cancelled
        │   │       │   └── cancelled.json
        │   │       ├── complete
        │   │       │   └── complete.json
        │   │       ├── customer_rejection
        │   │       │   └── customer_rejection.json
        │   │       ├── draft
        │   │       │   └── draft.json
        │   │       ├── escalated
        │   │       │   └── escalated.json
        │   │       ├── flagged
        │   │       │   └── flagged.json
        │   │       ├── hold
        │   │       │   └── hold.json
        │   │       ├── in_progress
        │   │       │   └── in_progress.json
        │   │       ├── inspection
        │   │       │   └── inspection.json
        │   │       ├── in_transit
        │   │       │   └── in_transit.json
        │   │       ├── new
        │   │       │   └── new.json
        │   │       ├── pending
        │   │       │   └── pending.json
        │   │       ├── qc
        │   │       │   └── qc.json
        │   │       ├── received
        │   │       │   └── received.json
        │   │       ├── repair
        │   │       │   └── repair.json
        │   │       ├── returned_to_customer
        │   │       │   └── returned_to_customer.json
        │   │       └── setup
        │   │           └── setup.json
        │   ├── inventory
        │   │   ├── doctype
        │   │   │   ├── __init__.py
        │   │   │   ├── pad_count_intake
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── pad_count_intake_api.py
        │   │   │   │   ├── pad_count_intake.js
        │   │   │   │   ├── pad_count_intake.json
        │   │   │   │   └── pad_count_intake.py
        │   │   │   └── pad_count_log
        │   │   │       ├── __init__.py
        │   │   │       ├── pad_count_log.json
        │   │   │       └── pad_count_log.py
        │   │   └── __init__.py
        │   ├── lab
        │   │   ├── api.py
        │   │   ├── config
        │   │   │   └── desktop.py
        │   │   ├── doctype
        │   │   │   ├── environment_log
        │   │   │   │   ├── environment_log.json
        │   │   │   │   ├── environment_log.py
        │   │   │   │   └── __init__.py
        │   │   │   ├── __init__.py
        │   │   │   ├── measurement_entry
        │   │   │   │   ├── measurement_entry.json
        │   │   │   │   └── measurement_entry.py
        │   │   │   └── measurement_session
        │   │   │       ├── measurement_session.json
        │   │   │       └── measurement_session.py
        │   │   ├── __init__.py
        │   │   ├── page
        │   │   │   ├── desk_tuner
        │   │   │   │   ├── desk_tuner.js
        │   │   │   │   ├── desk_tuner.json
        │   │   │   │   └── __init__.py
        │   │   │   ├── __init__.py
        │   │   │   └── lab_console
        │   │   │       ├── __init__.py
        │   │   │       ├── lab_console.js
        │   │   │       └── lab_console.json
        │   │   ├── README.md
        │   │   └── tasks.py
        │   ├── logger.py
        │   ├── logs
        │   ├── modules.txt
        │   ├── ONBOARDING.md
        │   ├── optimize
        │   │   ├── __init__.py
        │   │   └── scan.py
        │   ├── package.json
        │   ├── patches.txt
        │   ├── player_profile
        │   │   ├── doctype
        │   │   │   ├── __init__.py
        │   │   │   ├── player_equipment_preference
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── player_equipment_preference.json
        │   │   │   │   └── player_equipment_preference.py
        │   │   │   └── player_profile
        │   │   │       ├── __init__.py
        │   │   │       ├── player_profile.js
        │   │   │       ├── player_profile.json
        │   │   │       ├── player_profile.py
        │   │   │       ├── README.md
        │   │   │       └── test_player_profile.py
        │   │   ├── __init__.py
        │   │   ├── notification
        │   │   │   └── player_not_linked
        │   │   │       └── player_not_linked.json
        │   │   ├── README.md
        │   │   ├── workflow
        │   │   │   ├── player_profile_setup
        │   │   │   │   └── player_profile_setup.json.bak-2025-07-27
        │   │   │   └── player_profile_workflow
        │   │   │       └── player_profile_workflow.json
        │   │   └── workflow_state
        │   │       ├── active
        │   │       │   └── active.json
        │   │       ├── archived
        │   │       │   └── archived.json
        │   │       └── linked_to_client
        │   │           └── linked_to_client.json
        │   ├── public
        │   │   ├── dist
        │   │   │   └── js
        │   │   │       ├── import_mapping_setting_autofill.bundle.V64U7T6Y.js
        │   │   │       ├── import_mapping_setting_autofill.bundle.V64U7T6Y.js.map
        │   │   │       ├── index.bundle.ZD2LQDO2.js
        │   │   │       ├── index.bundle.ZD2LQDO2.js.map
        │   │   │       ├── technician_dashboard.bundle.BK7VGC3I.js
        │   │   │       └── technician_dashboard.bundle.BK7VGC3I.js.map
        │   │   ├── images
        │   │   │   └── svg_pad_maps
        │   │   │       └── clarinet_upper_joint.svg
        │   │   ├── js
        │   │   │   ├── import_mapping_setting_autofill.bundle.js
        │   │   │   ├── import_mapping_setting_autofill.js
        │   │   │   ├── note_autocorrect.js
        │   │   │   ├── technician_dashboard
        │   │   │   │   ├── App.vue
        │   │   │   │   ├── index.bundle.js
        │   │   │   │   └── technician_dashboard.bundle.js
        │   │   │   └── tone_processor.js
        │   │   └── node_modules -> /home/frappe/frappe-bench/apps/repair_portal/node_modules
        │   ├── qa
        │   │   ├── config
        │   │   │   └── desktop.py
        │   │   ├── dashboard_chart
        │   │   │   ├── average_dp_trend.json
        │   │   │   ├── pass_rate_trend.json
        │   │   │   ├── qa_failures_by_tech.json
        │   │   │   ├── README.md
        │   │   │   └── re_service_rate_trend.json
        │   │   ├── data
        │   │   │   └── clarinet_qc.json
        │   │   ├── doctype
        │   │   │   ├── final_qa_checklist
        │   │   │   │   ├── final_qa_checklist.json
        │   │   │   │   ├── final_qa_checklist.py
        │   │   │   │   └── README.md
        │   │   │   └── final_qa_checklist_item
        │   │   │       ├── final_qa_checklist_item.json
        │   │   │       ├── final_qa_checklist_item.py
        │   │   │       └── __init__.py
        │   │   ├── __init__.py
        │   │   ├── notification
        │   │   │   ├── critical_fail_notification
        │   │   │   │   └── critical_fail_notification.json
        │   │   │   ├── follow_up_due_notification
        │   │   │   │   └── follow_up_due_notification.json
        │   │   │   ├── ncr_overdue_notification
        │   │   │   │   └── ncr_overdue_notification.json
        │   │   │   └── README.md
        │   │   ├── print_format
        │   │   │   ├── __init__.py
        │   │   │   ├── qc_certificate
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── qc_certificate.json
        │   │   │   ├── quality_inspection
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── quality_inspection.json
        │   │   │   └── README.md
        │   │   ├── README.md
        │   │   └── setup
        │   │       └── __init__.py
        │   ├── README.md
        │   ├── READMEs.md
        │   ├── repair
        │   │   ├── doctype
        │   │   │   ├── default_operations
        │   │   │   │   ├── default_operations.js
        │   │   │   │   ├── default_operations.json
        │   │   │   │   ├── default_operations.py
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── test_default_operations.py
        │   │   │   ├── __init__.py
        │   │   │   ├── operation_template
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── operation_template.json
        │   │   │   │   └── operation_template.py
        │   │   │   ├── pulse_update
        │   │   │   │   ├── pulse_update.json
        │   │   │   │   └── pulse_update.py
        │   │   │   ├── repair_feedback
        │   │   │   │   ├── repair_feedback.json
        │   │   │   │   └── repair_feedback.py
        │   │   │   ├── repair_issue
        │   │   │   │   ├── repair_issue.json
        │   │   │   │   └── repair_issue.py
        │   │   │   ├── repair_order
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── README.md
        │   │   │   │   ├── repair_order.js
        │   │   │   │   ├── repair_order.json
        │   │   │   │   ├── repair_order.py
        │   │   │   │   └── test_repair_order.py
        │   │   │   ├── repair_request
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── repair_request.js
        │   │   │   │   ├── repair_request.json
        │   │   │   │   ├── repair_request.py
        │   │   │   │   └── test_repair_request.py
        │   │   │   └── repair_task
        │   │   │       ├── __init__.py
        │   │   │       ├── repair_task.json
        │   │   │       └── repair_task.py
        │   │   ├── email
        │   │   │   └── feedback_request.html
        │   │   ├── __init__.py
        │   │   ├── notification
        │   │   │   └── material_reorder_warning
        │   │   │       └── material_reorder_warning.json
        │   │   ├── README.md
        │   │   ├── report
        │   │   │   ├── repair_issue_report
        │   │   │   │   ├── repair_issue_report.json
        │   │   │   │   └── repair_issue_report.py
        │   │   │   ├── repair_revenue_vs_cost
        │   │   │   │   ├── repair_revenue_vs_cost.json
        │   │   │   │   └── repair_revenue_vs_cost.py
        │   │   │   └── technician_utilization
        │   │   │       ├── technician_utilization.json
        │   │   │       └── technician_utilization.py
        │   │   ├── scheduler.py
        │   │   ├── tests
        │   │   │   └── test_repair_order.py
        │   │   └── web_form
        │   │       └── repair_request
        │   │           └── repair_request.json
        │   ├── repair_logging
        │   │   ├── config
        │   │   │   └── desktop.py
        │   │   ├── custom
        │   │   │   ├── customer_interaction_timeline.js
        │   │   │   ├── __init__.py
        │   │   │   └── item_interaction_timeline.js
        │   │   ├── dashboard_chart
        │   │   │   └── repair_tasks_by_day
        │   │   │       └── repair_tasks_by_day.json
        │   │   ├── doctype
        │   │   │   ├── barcode_scan_entry
        │   │   │   │   ├── barcode_scan_entry.json
        │   │   │   │   ├── barcode_scan_entry.py
        │   │   │   │   └── __init__.py
        │   │   │   ├── diagnostic_metrics
        │   │   │   │   ├── diagnostic_metrics.json
        │   │   │   │   ├── diagnostic_metrics.py
        │   │   │   │   └── __init__.py
        │   │   │   ├── __init__.py
        │   │   │   ├── instrument_interaction_log
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── instrument_interaction_log.json
        │   │   │   │   └── instrument_interaction_log.py
        │   │   │   ├── key_measurement
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── key_measurement.json
        │   │   │   │   └── key_measurement.py
        │   │   │   ├── material_use_log
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── material_use_log.json
        │   │   │   │   └── material_use_log.py
        │   │   │   ├── pad_condition
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── pad_condition.json
        │   │   │   │   └── pad_condition.py
        │   │   │   ├── related_instrument_interaction
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── related_instrument_interaction.json
        │   │   │   │   └── related_instrument_interaction.py
        │   │   │   ├── repair_parts_used
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── repair_parts_used.json
        │   │   │   │   └── repair_parts_used.py
        │   │   │   ├── repair_task_log
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── repair_task_log.json
        │   │   │   │   └── repair_task_log.py
        │   │   │   ├── tenon_measurement
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── tenon_measurement.json
        │   │   │   │   └── tenon_measurement.py
        │   │   │   ├── tone_hole_inspection_record
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── tone_hole_inspection_record.js
        │   │   │   │   ├── tone_hole_inspection_record.json
        │   │   │   │   └── tone_hole_inspection_record.py
        │   │   │   ├── tool_usage_log
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── tool_usage_log.json
        │   │   │   │   └── tool_usage_log.py
        │   │   │   ├── visual_inspection
        │   │   │   │   ├── visual_inspection.json
        │   │   │   │   └── visual_inspection.py
        │   │   │   └── warranty_modification_log
        │   │   │       ├── warranty_modification_log.json
        │   │   │       └── warranty_modification_log.py
        │   │   ├── __init__.py
        │   │   ├── module_def
        │   │   │   └── repair_portal.json
        │   │   ├── number_card
        │   │   │   ├── closed_service_logs
        │   │   │   │   └── closed_service_logs.json
        │   │   │   ├── in_progress_service_logs
        │   │   │   │   └── in_progress_service_logs.json
        │   │   │   └── open_service_logs
        │   │   │       └── open_service_logs.json
        │   │   ├── print_format
        │   │   │   └── instrument_tracker_log
        │   │   │       └── instrument_tracker_log.json
        │   │   ├── README.md
        │   │   ├── report
        │   │   │   └── repair_tasks_by_type
        │   │   │       ├── repair_tasks_by_type.json
        │   │   │       └── repair_tasks_by_type.py
        │   │   ├── workflow
        │   │   │   ├── repair_task_workflow
        │   │   │   │   └── repair_task_workflow.json
        │   │   │   └── service_log_workflow
        │   │   │       └── service_log_workflow.json
        │   │   └── workflow_state
        │   │       ├── closed
        │   │       │   └── closed.json
        │   │       ├── draft
        │   │       │   └── draft.json
        │   │       ├── in_progress
        │   │       │   └── in_progress.json
        │   │       ├── open
        │   │       │   └── open.json
        │   │       ├── resolved
        │   │       │   └── resolved.json
        │   │       └── submitted
        │   │           └── submitted.json
        │   ├── repair_portal
        │   │   ├── config
        │   │   │   └── desktop.py
        │   │   ├── doctype
        │   │   │   ├── pulse_update
        │   │   │   │   ├── __init__.py
        │   │   │   │   └── pulse_update.py
        │   │   │   ├── qa_checklist_item
        │   │   │   │   ├── qa_checklist_item.json
        │   │   │   │   └── qa_checklist_item.py
        │   │   │   └── technician
        │   │   │       ├── technician.js
        │   │   │       ├── technician.json
        │   │   │       └── technician.py
        │   │   ├── __init__.py
        │   │   ├── report
        │   │   │   └── technician_task_summary
        │   │   │       ├── technician_task_summary.json
        │   │   │       └── technician_task_summary.py
        │   │   ├── tests
        │   │   │   └── test_import_mapping_setting.py
        │   │   └── workspace
        │   │       └── repair_portal
        │   │           └── repair_portal.json
        │   ├── repair_portal_settings
        │   │   ├── doctype
        │   │   │   ├── import_mapping_setting
        │   │   │   │   ├── import_mapping_setting.js
        │   │   │   │   └── __init__.py
        │   │   │   ├── __init__.py
        │   │   │   └── repair_portal_settings
        │   │   │       ├── __init__.py
        │   │   │       ├── repair_portal_settings.js
        │   │   │       ├── repair_portal_settings.json
        │   │   │       ├── repair_portal_settings.py
        │   │   │       └── test_repair_portal_settings.py
        │   │   └── __init__.py
        │   ├── scripts
        │   │   ├── audit_doctypes.py
        │   │   ├── doctype_loader.py
        │   │   ├── hooks
        │   │   │   ├── clarinet_qc.py
        │   │   │   ├── __init__.py
        │   │   │   └── reload_all_doctypes.py
        │   │   ├── __init__.py
        │   │   ├── item_group_loader.py
        │   │   ├── json_loader.py
        │   │   ├── naming_audit.py
        │   │   ├── pre_migrate_check.py
        │   │   ├── reload_all_jsons.py
        │   │   ├── schema_guard.py
        │   │   └── schemas
        │   │       ├── brand_bundled.json
        │   │       ├── _departments.json
        │   │       ├── _holiday_list_fed_2025.json
        │   │       ├── _instrument_category_input.json
        │   │       ├── _instrument_model_import.json
        │   │       ├── __item_groups.json
        │   │       ├── _pad_maps.json
        │   │       ├── setup_template_standard_a_clarinet.json
        │   │       ├── setup_template_standard_bb_clarinet.json
        │   │       └── setup_template_standard_eb_clarinet.json
        │   ├── service_planning
        │   │   ├── config
        │   │   │   └── desktop.py
        │   │   ├── dashboard_chart
        │   │   │   └── scheduled_service_tasks_by_day
        │   │   │       └── scheduled_service_tasks_by_day.json
        │   │   ├── doctype
        │   │   │   ├── estimate_line_item
        │   │   │   │   ├── estimate_line_item.json
        │   │   │   │   ├── estimate_line_item.py
        │   │   │   │   └── __init__.py
        │   │   │   ├── repair_estimate
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── repair_estimate.json
        │   │   │   │   └── repair_estimate.py
        │   │   │   ├── service_plan
        │   │   │   │   ├── service_plan.json
        │   │   │   │   └── service_plan.py
        │   │   │   ├── service_task
        │   │   │   │   ├── service_task.json
        │   │   │   │   └── service_task.py
        │   │   │   └── tasks
        │   │   │       ├── tasks.json
        │   │   │       └── tasks.py
        │   │   ├── __init__.py
        │   │   ├── report
        │   │   │   └── repair_bay_utilization
        │   │   │       ├── repair_bay_utilization.json
        │   │   │       └── repair_bay_utilization.py
        │   │   └── workflow_state
        │   │       ├── completed.json
        │   │       ├── in_progress.json
        │   │       └── scheduled.json
        │   ├── stock
        │   │   └── doctype
        │   │       ├── delivery_note
        │   │       │   └── delivery_note.py
        │   │       └── stock_entry
        │   │           └── stock_entry.py
        │   ├── templates
        │   │   ├── clarinet_initial_setup_certificate.html
        │   │   ├── __init__.py
        │   │   └── pages
        │   │       ├── __init__.py
        │   │       └── repair_pulse.html
        │   ├── __test__.py
        │   ├── tests
        │   │   └── test_api.py
        │   ├── tools
        │   │   ├── config
        │   │   │   └── desktop.py
        │   │   ├── dashboard_chart
        │   │   │   └── overdue_tools_by_type
        │   │   │       └── overdue_tools_by_type.json
        │   │   ├── doctype
        │   │   │   ├── tool
        │   │   │   │   ├── __init__.py
        │   │   │   │   ├── tool.json
        │   │   │   │   └── tool.py
        │   │   │   └── tool_calibration_log
        │   │   │       ├── tool_calibration_log.json
        │   │   │       └── tool_calibration_log.py
        │   │   ├── __init__.py
        │   │   ├── README.md
        │   │   ├── report
        │   │   │   └── overdue_tool_calibrations
        │   │   │       ├── overdue_tool_calibrations.json
        │   │   │       └── overdue_tool_calibrations.py
        │   │   ├── stock_tools.py
        │   │   ├── workflow
        │   │   │   └── tool_lifecycle
        │   │   │       └── tool_lifecycle.json
        │   │   ├── workflow_state
        │   │   │   ├── available
        │   │   │   │   └── available.json
        │   │   │   ├── out_for_calibration
        │   │   │   │   └── out_for_calibration.json
        │   │   │   └── retired
        │   │   │       └── retired.json
        │   │   └── workspace
        │   │       └── tools
        │   │           └── tools.json
        │   ├── trade_shows
        │   │   └── __init__.py
        │   ├── utils
        │   │   ├── api_security.py
        │   │   ├── database_optimizer.py
        │   │   ├── error_handler.py
        │   │   ├── SERIALS.md
        │   │   └── serials.py
        │   ├── www
        │   │   ├── frontend.html
        │   │   ├── pad_map.py
        │   │   └── repair_pulse.py
        │   └── yarn.lock
        ├── REPORT
        │   ├── inventory.md
        │   └── static_findings.md
        ├── ruff.toml
        ├── setup.py
        └── yarn.lock

        345 directories, 687 files
