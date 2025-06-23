# Upgrade Notes
- Ensure Node.js 18+ is installed. Current environment uses v22 which is compatible.
- Install bench and run `bench version` to verify Frappe 15 before migrating to v16.
- `apps.json` enables Vite build for this app; run `bench build --apps repair_portal` after installing dependencies.
- Pending: convert remaining portal templates to Vue SFCs and add SSR routing for each.
- OCR intake import requires `pytesseract` and `Pillow` packages on the server.
- New **Customer Sign-Off** DocType stores digital approvals; run `bench migrate` after pulling updates.
