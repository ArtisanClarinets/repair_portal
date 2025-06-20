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
- Added `scripts/sort_doctype_json.py` utility to alphabetically sort DocType
  JSON keys and nested lists. Run it with the path to any DocType JSON file to
  normalize field order before committing.

### 2024-06-19
- Migrated web controllers from `repair_portal/repair_portal/www` to `repair_portal/www`.
- Moved `repair_pulse.html` to `templates/pages/` and removed unused pad map templates.


## Enabling Pulse Update Feature
1. Run `bench migrate` to apply new DocTypes.
2. Use `/repair_pulse?name=REQ-0001` to view live updates.
3. Technicians call `pulse_update.create_update` API to post progress.
