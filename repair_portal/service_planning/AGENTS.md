# AGENTS.md — service_planning Module

## 🧮 Purpose
Supports advanced planning, custom quotes, and bundled service task mapping.

## 📁 Structure
- `doctype/service_plan/` — templated or ad-hoc estimate doc
- `doctype/upgrade_option/` — child table for upsell

## 💼 Responsibilities
- Map service options to cost estimate and labor plan
- Permit technician edits but lock down upon client approval

## 🧠 Agent Notes
- Add method `add_custom_item()` to append upgrades to a plan
- Used in `/repair_request` quote builder frontend
- Emit event if client accepts quote

## 🧪 Validation
- Validate cost fields are populated
- Auto-calculate total estimate on `validate()`