## Doctype: Client Instrument Profile

### 1. Overview and Purpose

**Client Instrument Profile** is a doctype in the **Instrument Profile** module that manages and tracks related business data.

**Module:** Instrument Profile
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `instrument_model` | Data | **Required** |
| `serial_no` | Link (Serial No) | **Required**, **Unique** |
| `instrument_category` | Select (Clarinet
Bass Clarinet
Contrabass Clarinet) | **Required** |
| `purchase_receipt` | Attach | Purchase Receipt |
| `external_work_logs` | Table (Customer External Work Log) | Previous Repairs |
| `condition_images` | Table (Instrument Photo) | Condition Images |
| `repair_preferences` | Small Text | Client Repair Preferences |
| `verification_status` | Select (Pending
Approved
Rejected) | Default: `Pending` |
| `technician_notes` | Text | Technician Review Notes |
| `ownership_transfer_to` | Link (Customer) | Transfer Ownership To |
| `anonymize_for_research` | Check | Default: `0` |
| `consent_log` | Table (Consent Log Entry) | Consent Log |
| `instrument_owner` | Link (Customer) | **Required** |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`client_instrument_profile.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_insert()`**: Runs before a new document is inserted
- **`on_update()`**: Runs after document updates
- **`on_trash()`**: Executes before document deletion

#### Frontend Logic (JavaScript)

The JavaScript file (`client_instrument_profile.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes
- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Serial No** doctype via the `serial_no` field (Serial Number)
- Has child table **Customer External Work Log** stored in the `external_work_logs` field
- Has child table **Instrument Photo** stored in the `condition_images` field
- Links to **Customer** doctype via the `ownership_transfer_to` field (Transfer Ownership To)
- Has child table **Consent Log Entry** stored in the `consent_log` field
- Links to **Customer** doctype via the `instrument_owner` field (Owner)

### 5. Critical Files Overview

- **`client_instrument_profile.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`client_instrument_profile.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`client_instrument_profile.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_client_instrument_profile.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
