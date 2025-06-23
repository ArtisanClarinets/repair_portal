# AGENTS.md — intake Module

## 📥 Purpose
Manages instrument intake, triage, and check-in flow. Ensures a chain of custody and clear condition logs.

## 📁 Structure
- `doctype/intake_form/` — client-submitted or technician intake entry
- `doctype/intake_photo/` — optional photo logs of condition

## ⚙️ Responsibilities
- Link to `Client` and `Instrument Profile`
- Generate Intake ID and date at creation
- Ensure intake can't be submitted if inspection is missing

## 🧠 Agent Notes
- Include checklist fields: case damage, tenon wear, loose rods
- Set workflow to enforce technician sign-off before advancing

## 🧪 Validation
- Reject form submission if no instrument linked
- Test flow from `/repair_request` to Intake submission