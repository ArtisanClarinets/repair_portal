# CHANGELOG – Clarinet Intake

## [v5.0] – 2025-07-21
### Major Refactor & Workflow Unification
- Fully orchestrated submission flow: always creates Instrument Inspection for all intake types.
- For `New Inventory`: creates Instrument, ERPNext Item, Serial No, and Clarinet Initial Setup.
- Naming, validation, and logic now fully settings-driven (no hardcoding).
- All fields, naming, and links (`instrument`) now fully synchronized backend and frontend.
- Dynamic field requiredness in both Python and JS, matching business rules.
- Robust error handling and logging for every orchestrated creation.
- Field `instrument_unique_id` is now `instrument` everywhere (backend and UI).
- Legacy `clarinet_intake_serial.py` officially deprecated—logic unified in controller.
- Settings, price lists, and warehouse links pulled only from `Clarinet Intake Settings`.

## [v4.3] – 2024-07-10
### Intake Workflow Expansion
- Added initial support for automatic creation of Instrument, Serial, and Setup for new inventory.
- First dynamic field mapping by intake type.

## [v4.0] – 2024-06-02
### Intake Logic Modularization
- Validation and core orchestration broken into helpers, decoupled from UI.
- Instrument Inspection always created on submit.

## [Older versions]
- See legacy GIT history for incremental schema/field patches prior to June 2024.

---

**Maintained by Priscilla – Frappe Engineer, 2024–2025**
