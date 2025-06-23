# AGENTS.md — client_profile Module

## 👤 Purpose
Stores all client-linked profile data including musicians, owners, and linked instruments.

## 📁 Structure
- `doctype/client_profile/` — main profile for an individual
- `doctype/client_instrument_link/` — optional links to instruments

## ✨ Responsibilities
- Persist client metadata across repairs
- Expose safe read-only fields to client portal

## ⚠️ Agent Notes
- Validate all `Link` fields against system Doctypes
- Enforce `Client` role permissions on all views
- Add search fields (`first_name`, `last_name`, etc.) to speed up lookup
- Keep any portal-facing controllers secure with `only_for("Client")`

## 🧪 Validation
- Validate email, phone, and musician status if fields are added
- Run full tests from app root: `bench run-tests --app repair_portal`