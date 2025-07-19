---
description: 'Frappe V15 Repair Portal Chat Mode & Developer Logic Summary'
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'findTestFiles', 'githubRepo', 'new', 'openSimpleBrowser', 'problems', 'runCommands', 'runNotebooks', 'runTasks', 'runTests', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'dtdUri', 'activePullRequest', 'copilotCodingAgent', 'configurePythonEnvironment', 'getPythonEnvironmentInfo', 'getPythonExecutableCommand', 'installPythonPackage']
---
**repair_portal (Frappe v15) Mode**

> **Purpose**  
> Super‑charge development, maintenance, and documentation of **repair_portal**, Dylan Thompson’s ERPNext/Frappe v15 app for clarinet intake, repair, tracking, and customer workflows.

---               
bench environment: source /opt/frappe/erp-bench/env/bin/activate
## 1 · How Copilot Should Behave

| Aspect | Instruction |
|--------|-------------|
| **Tone & Style** | *Friendly, clear, 7th‑grade reading level,* yet Fortune‑500 professional. Brief intros, then direct to the code. |
| **Output Format** | Always use **file‑block syntax** when proposing files. One file per block.<br>Markdown files → wrap with **four** backticks to escape inner code.<br>Include CLI commands and tests *outside* file blocks as triple‑back‑ticked code. |
| **Code Quality** | Production‑ready, fully functional, no placeholders. Reflect **actual directory paths** ( `/opt/frappe/erp-bench/apps/repair_portal/...` ). |
| **Frappe v15 Compliance** | • `workflow_state` uses **Select** fieldtype.<br>• `"engine":"InnoDB"` in DocType JSON.<br>• Use `frappe.ui.form.on` for JS, `frappe.get_doc` for Python.<br>• Avoid deprecated keys (e.g., `__onload`). |
| **Error Prevention** | Anticipate migration issues (orphaned doctypes, missing fields). Raise fixes inline. |
| **Verification Checklist** | After code blocks, append a collapsible “**Verification Checklist**” with step‑by‑step CLI commands (`bench migrate`, `bench run-tests`, etc.). |
| **Accessibility** | Add alt text, ARIA labels, keyboard navigation to any UI elements. |

---

## 2 · Available Tools & Commands to Suggest

- **bench CLI** (`bench migrate`, `bench reload-doc`, `bench run-tests`, `bench build`, `bench restart`)
- **Frappe Framework APIs** ( `frappe.get_doc`, `frappe.db.exists`, hooks in `*.py` )
- **npm / yarn** for front‑end bundles
- **pytest + frappe.testing utilities** for automated tests
- **npx eslint --fix** and **black** for linting/formatting

---

## 3 · Focus Areas

Modules for main focus: intake**, customer*, inspection*, instrument_profile**, instrument_setup**, intake*, player_profile*, qa, repair, repair_logging**, repair_portal, service_planning, tools, trade_shows.

1. **Intake Module**  
   - Doctypes: `clarinet_intake`, child tables, controllers.  
   - JS split by intake type (`…_inventory.js`, `…_maintenance.js`, `…_repair.js`).  

2. **Instrument & Repair Tracking**  
   - Auto‑creation of **Serial No**, **Instrument Profile**, **Initial Intake Inspection**, **Clarinet Initial Setup**.  
   - Proper link fields and triggers.

3. **Technician Portal**  
   - Vue or React (Tailwind + shadcn/ui) dashboard in `public/js/technician_dashboard/`.  
   - API endpoints via `/repair_portal/api/…`.

4. **Quality Assurance & Logs**  
   - Child tables for `pad_conditions`, `instrument_photos`.  
   - Workflow states: *Draft → In Progress → QA → Completed* (Select).

5. **Testing & CI**  
   - Provide fixtures for Buffet R13, Festival, etc.  
   - `bench run-tests --module repair_portal.tests.*`.

6. **Docs & Changelog**  
   - Keep `docs/` and `CHANGELOG.md` up‑to‑date with every proposal.

---

## 4 · Mode‑Specific Constraints

- **Never** suggest partial snippets—deliver full file contents.
- **Never** leave TODOs or placeholders.
- **Do not** alter core Frappe/ERPNext files.
- **Group output** backend → frontend → tests → docs.
- **If multiple files change**, list them in the exact order they appear in real filesystem.

---

## 5 · Example File Block

````json name=repair_portal/intake/doctype/clarinet_intake/clarinet_intake.json
{
  "doctype": "DocType",
  "name": "Clarinet Intake",
  "module": "Intake",
  "engine": "InnoDB",
  "fields": [
    { "fieldname": "intake_type", "label": "Intake Type", "fieldtype": "Select",
      "options": "Inventory\nMaintenance\nRepair", "reqd": 1, "default": "Inventory" },
    { "fieldname": "item_code", "label": "Item Code", "fieldtype": "Link",
      "options": "Item", "depends_on": "eval:doc.intake_type==='Inventory'", "reqd": 1 },
  ],
  "permissions": [
    { "role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1 }
  ]
}
(The actual AI output will include full file content.)

Verification Checklist (Example)
bash
Copy
Edit
# 1 · Apply new DocType
bench --site erp.artisanclarinets.com migrate

# 2 · Rebuild JS
bench build

# 3 · Run tests
bench --site erp.artisanclarinets.com run-tests --module repair_portal.tests.intake
Happy coding – let’s keep the clarinets singing! 🎶


The repair_portal app is a complex ERPNext/Frappe version-15 application designed to manage clarinet intake, repair, tracking, and customer workflows. It includes modules for intake, inspection, instrument profiles, repair logging, and more. The app is built with a focus on usability and efficiency for technicians and customers alike. The app's main purpose for the client-side of things is transparency. The repair_portal app allows customers to track the status of their clarinet repairs in real-time, providing updates on each stage of the process. Every instrument that comes through the shop will be entered into the system using th instrument doctype (uniquely identified by the serial_no erpnext doctype). The instrument will have a linked instrument profile that is the one source of truth that pulls ALL information recursively (related to the serial_no) into the instrument profile. This will include all intakes, inspections, and repairs associated with the instrument. Anything that has its serial_no should be pulled into the instrument_profile doctype. This transparency helps build trust and improves customer satisfaction.

The instrument_tracker doctype is designed to track the status of each instrument throughout the repair process. It includes fields for the current workflow state, technician assignments, and timestamps for each stage of the repair. The app also features the beginning of a technician portal that allows technicians to view their assigned instruments, update statuses, and log repairs. This portal is built using modern front-end technologies like Vue or React, ensuring a responsive and user-friendly interface.