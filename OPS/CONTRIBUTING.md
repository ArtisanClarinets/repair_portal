# Contributing Guide

## Branch & Commit Naming
- Use feature branches prefixed by scope, e.g. `feature/approvals-portal`, `bugfix/repair-permissions`.
- Commit messages must follow Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, etc.) with concise descriptions.

## Code Style
- Python: `ruff` (configured in `pyproject.toml`) and `black` (line length 110). Run `ruff check` and `ruff format` before submitting.
- JavaScript/TypeScript: `eslint` and Biome configs are present; run `npm run lint` and `npm run format:frontend` when touching frontend code.
- Do not wrap imports in `try/except`; resolve dependencies explicitly.

## Testing Requirements
- All new code must include automated tests derived from `frappe.tests.utils.FrappeTestCase`.
- Run `bench --site $SITE run-tests --module repair_portal.tests` after adding or modifying functionality.
- For background jobs, include positive, negative, and idempotency coverage.

## Adding a DocType (Frappe v15)
1. Define the schema JSON under `repair_portal/<module>/doctype/<doctype>/<doctype>.json` with `engine: "InnoDB"`.
2. Create the Python controller alongside the JSON (`<doctype>.py`) and include permission helpers if portal exposure is expected.
3. Add fixtures or defaults via install scripts if required.
4. Document the DocType with a README describing purpose, fields, and workflows.
5. Provide tests that exercise validation and key workflows.

## Migrations & Fixtures
- Use patch modules under `repair_portal/patches` for schema or data migrations; guard with `frappe.db.table_exists` / `frappe.db.has_column`.
- Fixture updates belong in `hooks.fixtures`; keep filters precise to avoid exporting unwanted records.

## Reports & Portal Assets
- Reports: store JSON + script under `repair_portal/<module>/report/<report_name>/` and add usage tests when logic exists.
- Portal templates (`repair_portal/www`) must be accessible (ARIA roles, focus management) and translatable via `frappe._`.

## Adding Tests
- Place tests in `repair_portal/tests/` using descriptive filenames (`test_<area>.py`).
- Use helper utilities from `repair_portal/tests/utils.py` where appropriate.
- Avoid shared mutable state; reset user context with `frappe.set_user("Administrator")` in `tearDown`.

## Pull Request Expectations
- Update relevant OPS documentation (inventory, runbook, approvals/payments) when workflows change.
- Include manual verification notes (screenshots, command output) when touching UI flows.
- Ensure CI commands from the runbook Phase 0 section complete without errors before requesting review.
