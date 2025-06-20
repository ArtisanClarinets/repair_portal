# Repair Portal

## Update Log

### 2025-06-16
- Added Instrument Category DocType (`instrument_profile/doctype/instrument_category/`).
- Controller and JSON schema included for Instrument Category.
- Ensured all files present per Frappe v15 convention.
- Ready for migration.

### 2025-07-01
- Added Pulse Update feature with real-time repair tracking.

### 2024-06-19
- Migrated web controllers from `repair_portal/repair_portal/www` to `repair_portal/www`.
- Moved `repair_pulse.html` to `templates/pages/` and removed unused pad map templates.


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
