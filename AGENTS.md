# AGENTS.md — Contributor Guide for `repair_portal`

## 📦 Overview
This is the main app directory for the **Clarinet Repair Portal**, a custom ERPNext v15 module designed for MRW Artisan Instruments. All development should follow the modular pattern set by Frappe/ERPNext and respect production-grade standards.

- Main source path: `/opt/frappe/erp-bench/apps/repair_portal/`
- Key directories:
  - `repair_logging/` — pad maps, photo logs, repair updates
  - `repair/` — main repair workflow
  - `client_profile/`, `inspection/`, etc. — scoped modules
  - `www/` — Python controllers for website-facing pages
  - `templates/pages/` — public and user portal Jinja templates

## 🧪 Validation & Testing
- Activate the virtualenv:
  ```bash
  source /opt/frappe/erp-bench/env/bin/activate
  ```
- To validate changes:
  ```bash
  bench --site erp.artisanclarinets.com migrate
  bench --site erp.artisanclarinets.com clear-cache
  bench export-fixtures --app repair_portal
  bench run-tests --app repair_portal
  ```

## 🎨 Code Style
- Python: Format with `Black` (line length 110) and `Ruff`.
- Frontend: Use Vue3 + Tailwind where applicable.
- Always use full file headers with:
  - Relative path
  - Date updated
  - Version
  - Purpose & dev notes

## 🔒 Permissions & API
- Always wrap data-changing API calls with:
  ```python
  @frappe.whitelist(allow_guest=False, methods=["POST"])
  frappe.only_for(["Technician"])
  ```
- Use `frappe.safe_json.dumps()` for passing data to Jinja.

## 🧠 AGENT Instructions
- Recursively trace all DocType references.
- Validate JSON before writing.
- Never hallucinate paths — verify or ask.
- Update all `README.md` when modifying anything.
- Follow file scaffold shown in Frappe_App_Structure_Guide.json

---
For module-specific rules, see nested `AGENTS.md` in each module.
