# Repair Order (`repair_order`)

## Purpose

The **Repair Order** DocType is the central control document for managing the full lifecycle of instrument repair projects—covering intake, diagnostics, repair execution, quality assurance, billing, and analytics. It provides an ERPNext v15–ready, Fortune-500-grade framework for technicians, managers, and customers, with robust automation, data integrity, and audit-grade error logging.

---

## Schema Summary

### Identification & Basic Info

* **naming\_series** – Auto-generated ID (`RO-.YYYY.-`) for unique tracking
* **customer** – Link to the Customer initiating the repair
* **instrument\_profile** – Link to the Instrument Profile being serviced
* **company** – Company responsible for the repair
* **posting\_date** – Date the repair order is created (default: Today)
* **priority** – Select: Low, Medium (default), High, Critical
* **assigned\_technician** – User assigned to perform the repair
* **target\_delivery** – Target completion date

### Materials (Actual)

* **warehouse\_source** – Source warehouse for parts (required)
* **actual\_materials** – Child table (`Repair Actual Material`) that mirrors Stock Entry items to track actual materials used.

### Labor

* **labor\_item** – Service Item representing labor (required)
* **labor\_rate** – Hourly labor rate
* **total\_estimated\_minutes** – Aggregate of estimated minutes from Repair Task child rows
* **total\_actual\_minutes** – Aggregate of actual minutes from Repair Task child rows.

### Workflow Controls

* **qa\_required** – Boolean flag to enforce QA (default: 1)
* **require\_invoice\_before\_delivery** – Boolean flag requiring invoice before delivery
* **workflow\_state (RO Status)** – Read-only Select with states: Draft, In Progress, QA, Ready, Delivered, Closed
* **remarks** – Freeform notes.

### Permissions

* **Repair Manager** – Full CRUD and sharing rights
* **Repair Technician** – Read/Write but cannot create or delete
* **Sales User / Accounts User** – Read/Print/Email only.

---

## Business Rules & Server Logic (`repair_order.py`)

### Lifecycle & Validation

* **validate()**

  * Applies defaults from *Repair Settings* (company, warehouse, labor item/rate, QA flags).
  * Checks `status` against `ALLOWED_STATUS` list: Draft, Intake, Diagnostics, Structural, Pads & Sealing, Setup, QA, Ready for Pickup, Delivered, Cancelled.
  * Warns if Customer, Source Warehouse, or Labor Item are missing.
  * Normalizes first-class links (Clarinet Intake, Instrument Inspection, Service Plan, Repair Estimate, Measurement Session, Instrument Profile) into the Related Documents child table.
  * Deduplicates Related Documents.
  * Aggregates estimated/actual minutes from Repair Task child rows to update `total_estimated_minutes` and `total_actual_minutes`.

### Key Methods

* **create\_child(doctype)** – Returns route options to create a linked child document with pre-filled references.

### ERPNext Integrations

* **create\_material\_issue\_draft(repair\_order)** – Creates a draft **Stock Entry** (Material Issue) with RO reference in remarks for auto-linking.
* **refresh\_actuals\_from\_stock\_entry(repair\_order, stock\_entry)** – Mirrors submitted Stock Entry items into `actual_materials` for at-a-glance visibility; accounting remains in Stock Ledger.
* **generate\_sales\_invoice\_from\_ro(repair\_order)** – Generates a **Sales Invoice** that:

  * Adds all Actual Materials as parts.
  * Converts total actual minutes → hours and adds a labor line using `labor_item` and `labor_rate`.

### Hook for Automation

* **\_on\_submit\_stock\_entry(doc, method)** – Optional doc\_event hook to auto-mirror materials when a Stock Entry is submitted.

### Internal Utilities

* `_get_total_minutes_from_tasks_or_aggregate()` – Prefers aggregate field, else sums child tasks.
* `_extract_ro_from_se()` – Parses Stock Entry remarks and item descriptions to detect RO reference.

---

## Client Logic (`repair_order.js`)

### Form Events

* **refresh(frm)** – Adds *Create* shortcuts and ERPNext integration actions only for saved documents.

### Create Shortcuts

Quickly start related documents with RO, Customer, and Instrument Profile pre-filled:

* Clarinet Intake
* Instrument Inspection
* Service Plan
* Repair Estimate
* Final QA Checklist
* Measurement Session
* Repair Task.

### Integration Actions

* **Create Material Issue (Actuals)** – Calls `create_material_issue_draft` to draft a Stock Entry.
* **Generate Sales Invoice** – Calls `generate_sales_invoice_from_ro` to create a Sales Invoice.
* **Refresh Actuals from Stock Entry** – Prompts for a submitted Stock Entry, then mirrors its items into `actual_materials`.

All buttons feature user-friendly alerts, freeze messages, and error handling for Fortune-500-grade UX.

---

## Dashboard (`repair_order_dashboard.py`)

* Provides a simple dashboard linking all key stage doctypes—Clarinet Intake, Instrument Inspection, Service Plan, Repair Estimate, Final QA Checklist, Measurement Session, and Repair Task—for seamless navigation from a Repair Order.

---

## Data Integrity

### Required Fields

* `customer`, `warehouse_source`, `labor_item`, and `naming_series` must be set for key operations.

### Defaults

* Company, warehouse, labor item/rate, QA flags pulled automatically from **Repair Settings** if blank.

### Constraints

* `workflow_state` restricted to allowed states.
* Minutes fields are automatically aggregated; no manual edits.

### Referential Integrity

* Related documents normalized and deduplicated automatically.
* Actual Materials child table reflects submitted Stock Entries for consistent inventory tracking.

---

## Workflows & Roles

* **Repair Manager** drives the process from intake through delivery.
* **Technicians** update progress and material usage.
* **Sales/Accounts** handle invoicing and financial reports.
* Status transitions and QA gates follow internal policies defined in ERPNext Workflow, with optional hook to auto-mirror Stock Entry data.

---

## Test Plan

### Unit & Integration

* **Defaults & Validation:** Ensure defaults load from Repair Settings; invalid statuses are rejected.
* **Material Mirror:** Test `refresh_actuals_from_stock_entry` and `_on_submit_stock_entry` for accuracy.
* **Invoice Generation:** Confirm correct parts and labor lines in generated Sales Invoice.
* **Time Totals:** Verify minutes aggregation and hour conversion.

### Performance

* Stress test with high volumes of Repair Tasks and Actual Materials.
* Verify responsiveness of client-side actions and dashboard links.

---

## Changelog

* **2025-09-16** – v2.0.0: Major refactor with enhanced default settings, robust ERPNext integrations, and comprehensive client UX improvements.
* **2025-07-17** – Added error logging, customer read permission, and portal visibility.
* See `/CHANGELOG.md` for the full project history.


