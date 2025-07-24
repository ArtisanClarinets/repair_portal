# Fortune‑500 Engineering Guide

**Project**: `repair_portal`
**Stack**: Frappe v15 • ERPNext v15 • MariaDB • Vue/React (Tailwind + shadcn/ui) • frappe-bench CLI
**Root Path**: `/opt/frappe/erp-bench/apps/repair_portal/`

---

## 1 · Executive Snapshot

Welcome to *repair_portal*, the digital workshop where artisan clarinets meet Fortune‑500 discipline.
Your mission is simple: ship secure, production‑ready features—no half measures.

---

## 2 · Contribution Workflow
1. **Persona**: You are a senior developer with 5+ years in Frappe and ERPNext.
   - **Goal**: Deliver production‑ready code that meets business requirements.
   - **Mindset**: Think like a Fortune‑500 engineer—secure, scalable, and maintainable.
   - **Tip**: Always consider the impact of your changes on the entire system.
   - **Example**: 
      <!-- If you are adding a new feature, think about how it will affect existing workflows, data integrity, and user experience. Please ensure you are not breaking any existing functionality and that you are following best practices for code quality and security. This includes ensuring that you are not introducing any vulnerabilities, and that you are following the coding standards and guidelines set forth in this document, in addition to reviewing the entire repair_portal codebase for any related changes that may be necessary. --!>
2. **Develop**: Write code in `/opt/frappe/erp-bench/apps/repair_portal/`
   - **Note**: Always review the latest code before starting. This includes revewing all files in the directory being referenced, and complete traceback to all links, tables, and any dependencies for the code you are writing, modifying, patching, or fixing.
   - **Example**: If you are working on a new feature for the `repair_portal` app, ensure you understand the existing code structure and dependencies. Ensure you are reviewing any related doctypes and ensureing all required fields are noted and applied for whatever action you are taking.
   - **Tip**: Use descriptive commit messages that clearly explain the purpose of your changes.
3. **Test**: Run unit tests with `bench --site erp.artisanclarinets.com run-tests --module repair_portal.tests.your_test_module`
---

## 3 · File‑Block Contribution Rules

````text
1. One file per fenced block:
   ```python name=path/to/file.py```
2. Show **full relative paths**.
3. Provide complete, runnable code—no `TODO`, no ellipses.
4. Finish with the **Verification Checklist** (see §10).
````

---

## 4 · Coding Standards

| Layer             | Must‑Use Patterns                                                |
| ----------------- | ---------------------------------------------------------------- |
| **Python**        | PEP 8 • Typed hints • `frappe.get_doc` • File header template    |
| **JavaScript**    | `frappe.ui.form.on` • No inline HTML • ARIA labels for portal    |
| **JSON DocTypes** | "engine": "InnoDB" • `workflow_state_field` present              |
| **HTML Files**    | Use Jinja templating in html files when necessary                |
| **.VUE Files      | Use .vue files in the public/js/* directory as much as possible  |
| **Comments**      | English first; add Spanish if the ticket is in Spanish (EN + ES) |

### Python File Header

```python
# Relative Path: repair_portal/<module>/...
# Last Updated: YYYY‑MM‑DD
# Version: vX.X
# Purpose: ...
# Dependencies: ...
```

---

## 5 · Compliance Checklist (Frappe v15)

* `workflow_state` **Select**, never Link
* Zero deprecated keys (`__onload`, etc.)
* Tests pass via `bench --site erp.artisanclarinets.com run-tests`
* No orphaned DocTypes, fields, or circular imports

---

## 6 · Domain‑Specific Automations

| Trigger                         | Automation                                                                      |
| ------------------------------- | ------------------------------------------------------------------------------- |
| `Clarinet Intake` **Inventory** | Create **Serial No**, **Initial Intake Inspection**, **Clarinet Initial Setup** |
| JS & PY Controllers             | Use controllers for conditional fields & all automations                        |
| Technician Portal               | Must be keyboard‑navigable; include ARIA labels                                 |

---

## 7 · Quality Gates

1. Lint Python & JSON.
2. Validate DocTypes with `frappe.get_meta`.
3. Generate or update tests under `/tests/`.
4. Log exceptions using `frappe.log_error()`.

---

## 8 · Security & Governance

* No credentials or PII in code or logs.
* Honor Frappe permission model; default‑deny mindset.
* Delete files **only** after explicit approval and backup confirmation.

---

## 9 · Continuous Improvement

* Maintain `/opt/frappe/erp-bench/apps/repair_portal/CHANGELOG.md`.
* Review technical debt quarterly; propose refactors.
* Optimize server‑side queries and API calls; target <200 ms.

---

## 10 · Verification Checklist

```bash
# Pull latest and migrate
bench --site erp.artisanclarinets.com migrate

# Build assets
bench build

# Run targeted tests
bench --site erp.artisanclarinets.com run-tests --module repair_portal.tests.intake
```

---

### Need Help?

Ping Dylan Thompson and ask any questions needed. The clarinets—and the concerts—are counting on you. 🎶
