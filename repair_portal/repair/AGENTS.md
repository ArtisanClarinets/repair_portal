# AGENTS.md — repair Module

## 🔧 Purpose
Core repair logic and document workflows. All stages of clarinet service are managed here.

## 📁 Structure
- `doctype/repair_request/` — master repair document
- `workflow/` — governs the multi-step repair state machine

## 🔄 Responsibilities
- All repair logs, setup, and QA attach to this parent
- Use status fields for real-time progress and communication

## 🧠 Agent Notes
- Update `on_update()` to emit publish_realtime for `repair_status_update`
- Require `Client` and `Technician` roles for all portal routes
- Auto-generate Stripe link if balance due is present

## 🧪 Validation
- Must validate presence of `Instrument`, `Client`, `Intake`
- Ensure workflows match `workflow.json` transitions exactly