# AGENTS.md — instrument_profile Module

## 🎷 Purpose
Handles metadata and public-facing details for each clarinet. Supports canonical URLs for instrument passports.

## 📁 Structure
- `doctype/instrument_profile/` — WebsiteGenerator for individual instruments
- `doctype/instrument_part/` — linked table of components

## 🌐 Responsibilities
- Ensure `/instrument_profile/<name>` resolves correctly
- Support `published = 1` flag to toggle public access

## 🧠 Agent Notes
- Add `test_web_view.py` to validate all public routes
- If `published = 1`, sanitize all outbound JSON
- Secure updates to this doctype for `Technician` only

## 🧪 Validation
- Ensure proper `Link` to owner (Client)
- Run `bench run-tests --app repair_portal` after updates