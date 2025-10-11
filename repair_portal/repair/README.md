# Repair Module – MRW Artisan Instruments

**Last Updated:** 2024-10-01  
**Maintainer:** Artisan Clarinets Platform Team

---

## 📌 Purpose
Enterprise-grade orchestration for clarinet repair operations, covering the full lifecycle from intake and quotation through technician execution, QA, delivery, and revenue recognition. The module owns the Repair Order workflow, time/labor capture, materials ledger, SLA monitoring, QA gatekeeping, invoicing hand-offs, and dashboard experience for technicians and managers.

---

## 📁 Contents

### Key DocTypes
- `Repair Order` – Canonical job record with workflow state, SLA tracking, QA gate, materials, and billing status.
- `Repair Planned Material` / `Repair Actual Material` – Planned vs. consumed part usage.
- `Repair Labor Session` – Child table storing start/stop technician sessions with multipliers.
- `Repair Task`, `Repair Feedback`, `Repair Quotation` – Supporting operational flows.

### Workflows & Automation
- `workflow/repair_order_workflow.json` governs Requested → Quoted → In Progress → Ready for QA → Completed → Delivered transitions.
- Scheduler helpers (`repair/doctype/repair_order/repair_order.py` and `services/sla.py`) recalculate SLA status, generate escalations, and enforce pause/resume rules.
- Material consumption API issues a Stock Entry and mirrors the ledger into Actual Materials.

### UI & UX
- Desk form script (`repair_order.js`) provides workflow buttons, SLA controls, and invoicing/material actions.
- Dashboard surfaces SLA, QA, billing, and labor metrics; workspace cards surface technician queues (see `workspace/` directory).

---

## 🚀 Feature Highlights
- Deterministic workflow enforcement with illegal transition guardrails.
- Technician labor capture with overtime/rush multipliers and billable-hour rollups.
- One-click material consumption creating Material Issue Stock Entries and syncing Actual Materials.
- QA inspection enforcement before completion/delivery with timeline comments.
- SLA computation with automatic escalation emails when At Risk/Breached.
- Sales Invoice creation that bundles labor and consumed parts.

---

## 🧪 Testing
- `doctype/repair_order/test_repair_order.py` exercises workflow validation, QA enforcement, and billing helpers (requires bench runtime).
- Additional smoke tests live under `repair_logging/tests/` for cross-module telemetry.

Run with:
```bash
bench --site <yoursite> run-tests --doctype "Repair Order"
```

---

## 🔗 Integrations
- Links to `Clarinet Intake`, `Instrument Profile`, `Repair Task`, `Sales Invoice`, and Stock Entries.
- Auto-updates Player Profile customer linkage when applicable.
- Enqueue hooks coordinate with `repair_portal_settings` SLA defaults.

---

## 🛠 Admin Checklist
1. Ensure `Repair Settings` Single DocType has default Company, Source Warehouse, Labor Item, labor rate, and SLA Policy.
2. Review workflow permissions (Repair Manager, Repair Technician, Customer Service, QA Manager).
3. Configure email alerts for SLA escalations if not already enabled.
4. Periodically run the SLA monitor (`bench execute repair_portal.repair.doctype.repair_order.repair_order.monitor_open_orders`).
5. Audit Stock Entry mappings to confirm Actual Materials reflect warehouse consumption.
