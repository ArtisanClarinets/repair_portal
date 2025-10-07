## Doctype: Instrument Serial Number

### 1. Overview and Purpose

**Instrument Serial Number** is a doctype in the **Instrument Profile** module that manages and tracks related business data.

**Module:** Instrument Profile
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 1.1 ISN Strategy

- **Normalization Rules:** All user-supplied serials are uppercased, whitespace and punctuation are stripped, and repeated separators are collapsed. The canonical form is persisted on `normalized_serial` and is the value used for de-duplication.
- **Collision Policy:**
  - Blocking duplicates on the same Instrument is mandatory.
  - Across Instruments, duplicates are rejected when the Instruments share the same `brand`. Otherwise, a warning is issued and linkage decisions are deferred to technicians.
  - Unlinked ISNs with the same normalized value are mutually exclusive: the second insert fails until one record links to an Instrument.
- **Linking Precedence:** Instrument → ISN is authoritative. Controllers always attempt to attach the ISN back to the Instrument on insert/update to avoid drift. Serial utilities in `repair_portal/utils/serials.py` remain the single source of truth for normalization and candidate lookups.
- **Security Invariants:** Every mutating action requires `write` permission on both ISN and Instrument. Whitelisted helpers apply per-user rate limiting, log structured audit events to `instrument_profile_audit` / `instrument_profile_security`, and raise explicit `frappe.PermissionError` on violations. Enumeration attempts are throttled at 10 lookups per minute per user.

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `serial` | Data | **Required**. As stamped/engraved/printed on the instrument |
| `normalized_serial` | Data | Read-only. Uppercased, punctuation-stripped form used for matching |
| `serial_source` | Select (Stamped
Engraved
Etched
Label/Sticker
Handwritten
Unknown) | Default: `Etched` |
| `scan_code` | Data | Shop-applied scan code (optional) |
| `photo` | Attach Image | Serial Photo |
| `instrument` | Link (Instrument) | All instrument details live on Instrument |
| `erpnext_serial_no` | Link (Serial No) | Map to stock Serial No when the unit is on your books |
| `duplicate_of` | Link (Instrument Serial Number) | Mark this as a duplicate of another serial record |
| `verification_status` | Select (Unverified
Verified by Technician
Customer Reported
Disputed) | Default: `Unverified` |
| `verified_by` | Link (User) | Read-only |
| `verified_on` | Datetime | Read-only |
| `status` | Select (Active
Deprecated
Replaced
Error) | Default: `Active` |
| `notes` | Small Text | Notes |
| `linkage` | Heading | Linkage |
| `verification` | Heading | Verification |
| `isn_meta` | Heading | Meta |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instrument_serial_number.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_insert()`**: Runs before a new document is inserted
- **`after_insert()`**: Executes after a new document is created
- **`on_update()`**: Runs after document updates

**Custom Methods:**
- `attach_to_instrument()`: Custom business logic method
- `find_similar()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`instrument_serial_number.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes
- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument** doctype via the `instrument` field (Instrument)
- Links to **Serial No** doctype via the `erpnext_serial_no` field (ERPNext Serial No (Inventory))
- Links to **Instrument Serial Number** doctype via the `duplicate_of` field (Duplicate Of)
- Links to **User** doctype via the `verified_by` field (Verified By)

### 5. Critical Files Overview

- **`instrument_serial_number.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instrument_serial_number.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`instrument_serial_number.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_instrument_serial_number.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
