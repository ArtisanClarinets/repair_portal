# AGENTS.md — qa Module

## ✅ Purpose
Captures post-service quality assurance reviews, checklists, and client sign-off feedback.

## 📁 Structure
- `doctype/qa_check/` — internal QA logs
- `doctype/client_feedback/` — optional client portal feedback form

## 🎯 Responsibilities
- Must be timestamped and linked to final `Repair Request`
- Ensure client feedback is read-only after submission

## ⚠️ Agent Notes
- Run `qa_check.validate()` to ensure all steps are passed before submission
- Broadcast `qa_passed` event if all QA fields are marked ✓

## 🧪 Validation
- Enforce field dependencies (e.g., “pad height verified” requires “pads complete”)
- Test via UI and direct API using `frappe.client.submit()`