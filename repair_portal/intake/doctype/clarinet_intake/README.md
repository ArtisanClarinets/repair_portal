## Doctype: Clarinet Intake

### 1. Overview and Purpose

**Clarinet Intake** is a submittable DocType in the **Intake** module. It represents the enterprise-grade clarinet intake workflow from arrival through inspection, setup, repair, QA, and delivery, tracking SLA commitments and downstream automation.

**Module:** Intake  
**Type:** Submittable Document

This DocType is used to:
- Capture clarinet-specific metadata, logistics, and customer expectations at drop-off
- Trigger automation for serial numbers, instruments, inspections, setups, and consent forms
- Drive workflow transitions via `workflow_state`, including cancellation and escalation paths
- Surface SLA telemetry and loaner/accountability status through desk HTML widgets

### 2. Fields / Schema (Highlights)

| Field Name | Type | Description |
|------------|------|-------------|
| `intake_record_id` | Data (Unique, Read-only) | Deterministic naming field used for autoname (`field:intake_record_id`). |
| `intake_date` | Datetime (Read-only) | Defaults to `now`; stamped at creation for SLA tracking. |
| `intake_type` | Select | New Inventory / Repair / Maintenance. Drives dynamic mandatory rules. |
| `employee` | Link (User) | Assigned coordinator/technician; auto-set on creation. |
| `instrument` | Link (Instrument) | Linked instrument master when available. |
| `workflow_stage_badge` | HTML (Read-only) | Workflow-state visual badge rendered from `workflow_state` with clarinet-specific labels. |
| `sla_commitment_panel` | HTML (Read-only) | Inline SLA countdown, overdue banners, and escalation warnings. |
| `instrument_category` | Link (Instrument Category) | Required taxonomy link. |
| `manufacturer` | Link (Brand) | Required clarinet brand reference. |
| `model` | Data | Model information for analytics. |
| `serial_no` | Data | Required; unique constraint enforced via controller to avoid duplicates. |
| `clarinet_type` | Select | Clarinet family (B♭, A, E♭, Bass, Alto, Contra, Other). |
| `customers_stated_issue` | Small Text | Intake issue summary for technicians. |
| `arrival_transport_notes` | Small Text | Logistics notes (shipping, courier, handoff). |
| `risk_disclosures` | Small Text | Customer-provided risk disclosures (cracks, humidity). |
| `promised_completion_date` | Date | SLA anchor. Drives dashboard warnings. |
| `consent_form` | Link (Consent Form) | Auto-populated when consent automation enabled. |
| `instrument_condition_section` + condition fields | Section + Data/Select | Clarinet-specific condition scoring. |
| `initial_intake_photos` | Attach Image | Intake photography bundle. |
| `transport_photo_bundle` | Attach | Additional photo evidence captured via portal/web form. |
| `accessory_id` | Table (Intake Accessory Item) | Child table for mouthpieces, barrels, cases, etc. |
| `amended_from` | Link (Clarinet Intake) | Audit trail for amendments. |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_intake.py`) implements:
- `validate()` for dynamic mandatory checks, duplicate serial prevention, SLA defaults, and accessory integrity
- `on_submit()` to synchronize consent, inspection, setup, and instrument links
- `_should_create_consent()` / `_create_consent_form()` to automate customer consent flows
- Ownership enforcement and serial/instrument lookup methods leveraged by desk APIs

#### Frontend Logic (JavaScript)

`clarinet_intake.js` delivers:
- Workflow badge + SLA panel rendering tied to `workflow_state`
- Form refresh hooks that toggle field visibility, add clarinet-specific quick actions, and wire desk shortcuts
- API calls into `repair_portal.intake.api` for secure instrument lookups and inspection navigation

### 4. Relationships and Dependencies

- Links to **User** (`employee`)
- Links to **Instrument**, **Instrument Category**, **Brand**, **Customer**, **Work Order**, **Consent Form**
- Child table **Intake Accessory Item** for accessories on receipt
- Timeline integration with **Instrument Inspection**, **Clarinet Initial Setup**, and **Repair Order** records
- Workflow defined in `intake/workflow/intake_workflow/intake_workflow.json` (field `workflow_state`)

### 5. Critical Files Overview

- `clarinet_intake.json` — DocType schema definition (fields, permissions, dashboard)
- `clarinet_intake.py` — Controller automation (validation, linking, consent, ownership)
- `clarinet_intake.js` — Client-side UX (badges, SLA panels, quick actions, API calls)
- `clarinet_intake_list.js` — List view badges, filters, and bulk workflow actions
- `clarinet_intake_dashboard.py` & `clarinet_intake_timeline.py` — Desk analytics and heatmap data providers
- `test_clarinet_intake.py` — Unit tests covering automation and workflow states

---

*Last updated: 2025-10-05*
