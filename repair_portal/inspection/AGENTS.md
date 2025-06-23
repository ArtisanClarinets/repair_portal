# AGENTS.md — inspection Module

## 🔍 Purpose
Covers pre-repair inspections, visual assessments, and condition logs for incoming instruments.

## 📁 Structure
- `doctype/inspection_log/` — main inspection records
- `doctype/finding/` — individual defect notes (child)
- `report/` — inspector reports or trends

## 🛠️ Responsibilities
- Link every inspection to an `Instrument Profile`
- Trigger repair triage based on flagged conditions

## ⚠️ Agent Notes
- If `finding.severity = High`, escalate to `Repair Coordinator`
- Apply workflow if approval is required before intake
- Secure `POST` APIs with `@frappe.whitelist(allow_guest=False)`

## 🧪 Validation
- Cross-check `inspection_log.instrument` existence
- Add test coverage for edge cases like duplicate findings
- Use `frappe.throw` for missing critical fields