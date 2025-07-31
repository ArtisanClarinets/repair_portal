# Clarinet Intake Doctype Overview

## Files Reviewed
- clarinet_intake_timeline.py
- clarinet_intake.js
- clarinet_intake.py

## Purpose
Automates intake for new inventory, repairs, and maintenance. Ensures creation and linking of all related records (Item, Serial No, Instrument, Inspection, Initial Setup).

## Main Functions
### clarinet_intake_timeline.py
- Logs timeline entries for each auto-generated child record after intake creation.

### clarinet_intake.js
- Adds quick links to related settings and records (Inspection, Initial Setup).
- Dynamically toggles required fields based on intake type.
- Autofills instrument data from serial number.

### clarinet_intake.py
- `after_insert`: Automates creation of Item, Serial No, Instrument, Instrument Inspection, and Initial Setup records as needed.
- `autoname`: Generates unique intake record IDs.
- `validate`: Enforces dynamic mandatory fields and syncs info from existing instrument.
- Whitelisted methods for instrument lookup and inspection linking.

## Doctypes Created/Updated/Modified
- Creates/updates `Item`, `Serial No`, `Instrument`, `Instrument Inspection`, `Clarinet Initial Setup`.


