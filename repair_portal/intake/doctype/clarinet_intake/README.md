# Clarinet Intake Doctype — Logic & Automation Map

## Overview

**Clarinet Intake** is the gateway for all instruments entering the shop—whether Inventory or Repair. All workflows, automations, and UI rules are now split into inventory and repair modes for clarity, maintainability, and scalability. This README gives you (or any new developer) a comprehensive, up-to-date roadmap.

---

## What happens on save?

- **Inventory Intake**:
  - Shows and requires `item_code` and all core inventory fields
  - UI and validation logic handled in `clarinet_intake_inventory.bundle.js`
  - Auto-creates:
    - **ERPNext Serial No** (if not provided)
    - **Instrument Inspection**
    - **Clarinet Initial Setup**
  - All required fields are validated and users are prompted with friendly alerts if missing
  - Intake status badge shown on Desk form (Pending, In Progress, Complete)
- **Repair Intake**:
  - Hides inventory-specific fields and only shows repair-relevant ones
  - Validates required repair fields (e.g. consent form)
  - Consent/phone/email validation is enforced
  - No auto-creation (yet), but logic can be extended in `clarinet_intake_repair.py`
  - Intake status badge shown on Desk form (Pending, In Progress, Complete)

---

## File Map & Roles

| File                                                  | Role                                                                                         |
|-------------------------------------------------------|----------------------------------------------------------------------------------------------|
| `clarinet_intake.json`                                | Field schema and permission model. Adds item_code for Inventory.                             |
| `clarinet_intake.py`                                  | Main router — delegates to intake-type helper.                                               |
| `clarinet_intake_inventory.py`                        | Inventory: business rules (serial, setup, inspection auto-creation, error logging).          |
| `clarinet_intake_repair.py`                           | Repair: (currently minimal), future repair automation.                                       |
| `public/js/intake/clarinet_intake_inventory.bundle.js`| Desk logic for Inventory intake: field toggling, validation, indicators, and alerts.         |
| `public/js/intake/clarinet_intake_repair.bundle.js`   | Desk logic for Repair intake: field toggling, validation, consent alerts, and indicators.    |
| `hooks.py`                                            | Loads both JS files for Clarinet Intake (via doctype_js).                                    |
| `tests/test_inventory_intake.py`                      | Automated test: ensures automation works for Inventory intake.                               |

---

## Workflow — Step by Step

1. **User picks Intake Type** (Inventory or Repair)
2. If **Inventory**:
    - All inventory fields (item_code, brand, model, etc.) are shown and required
    - On save:
      - Serial No is created/linked
      - Instrument Inspection created
      - Clarinet Initial Setup created
      - Desk form gives visual status indicators
      - All validation and required prompts are enforced
3. If **Repair**:
    - Only repair-relevant fields shown
    - Consent form is validated
    - Desk form gives visual status indicators
    - No child automation by default (extend as needed)

---

## How to Extend
- Want to add automation for Repairs? Use `clarinet_intake_repair.py`.
- Want to add fields? Edit `clarinet_intake.json` and update the matching JS (bundle).
- All server-side automation should be wrapped in try/except and use `frappe.log_error()` per best practice.
- Update or add new tests in `tests/` for any new automation.

---

## Test Coverage
- Run tests in `tests/test_inventory_intake.py` to ensure all business rules are live.
- Add new tests for any extended or custom workflow.

---

## CLI for DevOps
```sh
cd /opt/frappe/erp-bench/
source env/bin/activate
bench --site erp.artisanclarinets.com migrate
bench build
```

---

## Gotchas & Tips
- Only the router (`clarinet_intake.py`) is loaded by Frappe as the DocType controller. Mode-specific logic must live in the helpers.
- Always update both backend and frontend when adding new required fields, validations, or UI logic.
- For new automations, create a test in `tests/`, and update the README and CHANGELOG.
- All indicators now use supported Frappe Desk APIs (no deprecated badge calls).
- Field toggling and validation are now Fortune-500 clean and split by mode (inventory/repair).
