## 2025-07-16
- Patched 7 Doctypes used in Client Profile: now correctly flagged as child tables with `parent` field.
- Fixed OperationalError on loading Client Profile due to missing `parent` columns.
- Extended Client Profile: now auto-creates ERPNext Customer on submit.
- Added fallback contact and address linkage during customer creation.
- Created `DEV.md` for Client Profile with complete dev guide and lifecycle notes.

## 2025-07-14
- Inventory intake automation updated: Now creates and links Clarinet Initial Setup, not Repair Order.
- Added/confirmed fields to link Intake, Setup, Instrument Profile (bidirectional).
- Updated test cases for intake and setup flows.
- Updated desk client script for intake.
- Robust error logging added.
- Added validation for required linkages.
- Created dev summary for future developers.
