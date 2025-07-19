## 2025-07-19
- Replaced all legacy references to **Initial Intake Inspection** with **Instrument Inspection** across all doctypes, controllers, tests, and onboarding documentation.
- Patched Instrument Profile doctype and controller to use Instrument Inspection for compliance and reporting.
- Updated Clarinet Intake README and tests for new naming and business rules.
- All intake and instrument automation now Fortune-500 compliant and Frappe v15 ready.

**Files updated:**
- instrument_profile/doctype/instrument_profile/instrument_profile.json
- instrument_profile/doctype/instrument_profile/instrument_profile.py
- intake/doctype/clarinet_intake/tests/test_inventory_intake.py
- intake/doctype/clarinet_intake/README.md

---

## 2025-07-19
- Major: Inventory intake now enforces **Item Code** and **Item Name** (required fields) in schema, backend, and frontend for new ERPNext Item creation.
- All Serial No and Instrument creation now link to the user-provided Item Code when available (fallback mapping used only for legacy/test cases).
- Instrument creation logic links the Instrument to the Item for full ERP traceability.
- All frontend toggling and validation now include item fields, blocking incomplete submissions at Desk.
- Code, comments, and validation updated to Fortune-500, Frappe v15, and security standards.

**Files updated:**
- intake/doctype/clarinet_intake/clarinet_intake.json
- intake/doctype/clarinet_intake/clarinet_intake.py
- intake/doctype/clarinet_intake/clarinet_intake_serial.py
- intake/doctype/clarinet_intake/clarinet_intake.js

---

## 2025-07-19
- All Clarinet Intake submissions now **automatically create a linked Instrument Inspection** (if one doesn't already exist for this intake+instrument).
    - Inspection is linked to Intake, Instrument, and Serial No.
    - Inspection type is set to **Initial Inspection** for Inventory, or **Arrival Inspection** for Repair/Maintenance.
    - Status set to **Open**.
- No duplicate inspections created per intake.
- Fully tested and exception-logged. No business logic lost in upgrade.

**Files updated:**
- intake/doctype/clarinet_intake/clarinet_intake.py

---

