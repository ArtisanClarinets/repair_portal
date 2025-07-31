# Instrument Inspection Doctype Overview

## Files Reviewed
- instrument_inspection.js
- instrument_inspection.py

## Purpose
Manages the lifecycle of instrument inspections for inventory, repair, maintenance, and QA. Automates field visibility, enforces business rules, and syncs inspection data to instrument profiles.

## Main Functions
### instrument_inspection.js
- Dynamically toggles field visibility based on inspection type.
- Ensures customer/pricing fields are hidden for inventory intake.
- Shows/hides fields for manufacturer/model/key/wood and overall condition.

### instrument_inspection.py
- `validate`: Enforces required fields, uniqueness of serial numbers, and correct field usage per inspection type.
- `_validate_unique_serial`: Ensures no duplicate serial numbers across inspections.
- `on_submit`: Syncs inspection data to the corresponding Instrument Profile, updating or creating the profile as needed.

## Doctypes Created/Updated/Modified
- Updates/creates `Instrument Profile` on submit.
- Validates and logs exceptions for audit.
