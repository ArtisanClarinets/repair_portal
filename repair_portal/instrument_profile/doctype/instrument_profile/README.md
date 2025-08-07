# Instrument Profile Doctype Overview

## Files Reviewed
- instrument_profile_list.js
- instrument_profile.js
- instrument_profile.py

## Purpose
Manages instrument profiles, linking them to ERPNext Serial Numbers and aggregating all related logs (repairs, inspections, setups, QA, warranty).

## Main Functions
### instrument_profile_list.js
- Customizes list view to prioritize serial number and status indicators.

### instrument_profile.js
- Adds dashboard indicators for status, verification, workflow, and warranty expiration.
- Provides workflow action buttons.

### instrument_profile.py
- `on_update`: Syncs ERPNext Serial No, warranty expiration, and populates all related logs as child tables.
- Auto-populates linked records for repairs, inspections, setups, QA, condition logs, external work, warranty, material usage, lab readings, document history, and interactions.

## Doctypes Created/Updated/Modified
- Links and syncs with `Serial No`, `Repair Log`, `Instrument Inspection`, `Clarinet Setup Log`, `Instrument Condition Record`, `External Work Logs`, `Warranty Modification Log`, `Material Use Log`, `Leak Test`, `Instrument Document History`, `Instrument Interaction Log`.
