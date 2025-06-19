# Repair Portal

## Update Log

### 2025-06-16
- Added Instrument Category DocType (`instrument_profile/doctype/instrument_category/`).
- Controller and JSON schema included for Instrument Category.
- Ensured all files present per Frappe v15 convention.
- Ready for migration.

### 2025-07-01
- Added Pulse Update feature with real-time repair tracking.


## Enabling Pulse Update Feature
1. Run `bench migrate` to apply new DocTypes.
2. Use `/repair_pulse?name=REQ-0001` to view live updates.
3. Technicians call `pulse_update.create_update` API to post progress.
