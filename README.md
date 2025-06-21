# Repair Portal

## Update Log

### 2025-06-16
- Added Instrument Category DocType (`instrument_profile/doctype/instrument_category/`).
- Controller and JSON schema included for Instrument Category.
- Ensured all files present per Frappe v15 convention.
- Ready for migration.

### 2025-07-01
- Added Pulse Update feature with real-time repair tracking.

### 2025-07-02
- Added `scripts/sort_doctype_json.py` utility to alphabetically sort DocType JSON keys and nested lists. Run it with the path to any DocType JSON file to normalize field order before committing.

### 2025-07-03
- Completed full production implementation of all scoped Repair Portal features:
  - Customer Sign-Off Portal (media, signature, workflow, shipping integration).
  - Defect Heat-Map dashboard and backend aggregation.
  - Certificate of Service PDF with QR/meta options.
  - Full Service Planning Suite (predictive, component lifespan, school planner, reminder workflows).
  - Instrument Profile modules: Timeline, Valuation, Upgrade Wishlist, Ownership transfer.
  - Full Client Portal: Unified chat, progress tracker, referrals, notifications.
  - Tools: Tuner, Bore Scanner, Adhesive timer, Pad kit builder.
  - Bench Ops: Screw Map, Kanban, Video training.

## Enabling Pulse Update Feature
1. Run `bench migrate` to apply new DocTypes.
2. Use `/repair_pulse?name=REQ-0001` to view live updates.
3. Technicians call `pulse_update.create_update` API to post progress.

## Development

### Frontend
Run `npm run dev` to launch Vite in development mode. Production assets are built via `bench build --apps repair_portal` which consumes `vite.config.ts`.

### Intake OCR Import
To convert handwritten intake forms into ERPNext documents:
1. Upload the scanned PDF or image to the File DocType.
2. Call `frappe.call('repair_portal.intake.import_handwritten_intake', {file_id})`.
3. A new **Clarinet Intake** record will be created with fields populated from OCR.

### Customer Sign-Off Portal
After repairs are completed, clients can digitally approve the job:
1. Visit `/customer_sign_off?repair=REQ-0001`.
2. Sign in the provided canvas area.
3. The signature is saved to a **Customer Sign-Off** record and shipping labels become available.

## Docs Per Module
Each module folder now contains a `README.md` listing:
- All implemented features.
- Available DocTypes.
- Integration points.
- Usage or testing notes where relevant.

This ensures every module is self-documented and follows Frappe v15 architecture cleanly.
