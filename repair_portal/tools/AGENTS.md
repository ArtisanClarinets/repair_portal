# AGENTS.md — tools Module

## 🧰 Purpose
Internal utilities, data migrations, and helpers that power behind-the-scenes logic.

## 📁 Structure
- `doctype/data_tool/` — import/export or batch actions
- `page/openwind/` — bindings for acoustics utility

## 🔒 Responsibilities
- Not client-facing
- Used only by System Manager or Technician roles

## 🧠 Agent Notes
- Never expose these routes without a login session
- Avoid adding business logic — tools only

## 🧪 Validation
- Test helpers via unit test + page interaction
- Mock necessary Frappe context if running stand-alone