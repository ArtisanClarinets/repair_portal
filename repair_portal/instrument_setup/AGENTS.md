# AGENTS.md — instrument_setup Module

## 🛠️ Purpose
Handles post-repair setup, technician review, and mechanical regulation.

## 📁 Structure
- `doctype/setup_checklist/` — table of technician sign-offs
- `doctype/setup_photo/` — optional final photo capture

## ✅ Responsibilities
- Ensure setup is only editable by assigned technician
- Must validate that all checkboxes are marked before submit

## ⚠️ Agent Notes
- Tie final QC to `Repair Request` via `Link` field
- Emit final status via `publish_realtime()` when setup completes

## 🧪 Validation
- Validate `play_tested = 1` before allow submit
- Ensure `bench run-tests --app repair_portal` includes full coverage