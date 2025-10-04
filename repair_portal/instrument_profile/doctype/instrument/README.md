## Doctype: Instrument

### 1. Overview and Purpose

**Instrument** is a doctype in the **Instrument Profile** module that manages and tracks related business data.

**Module:** Instrument Profile
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `instrument_id` | Data | **Unique**, Read-only. Automatically generated unique Instrument ID |
| `serial_no` | Data | **Required**, **Unique** |
| `instrument_type` | Select (B♭ Clarinet
A Clarinet
Bass Clarinet
E♭ Clarinet
Alto Clarinet
Contrabass Clarinet
Other) | Instrument Type |
| `brand` | Link (Brand) | Brand |
| `model` | Data | Model |
| `clarinet_type` | Select (B♭ Clarinet
A Clarinet
E♭ Clarinet
Bass Clarinet
Alto Clarinet
Contrabass Clarinet
Other) | **Required** |
| `body_material` | Data | Body Material |
| `keywork_plating` | Data | Keywork Plating |
| `pitch_standard` | Data | Pitch Standard |
| `year_of_manufacture` | Int | Year of Manufacture |
| `key_plating` | Select (Silver
Nickel
Gold
Other) | Key Plating |
| `instrument_category` | Link (Instrument Category) | Instrument Category |
| `current_status` | Select (Active
Needs Repair
Awaiting Parts
In Service
Archived) | Default: `Active` |
| `notes` | Small Text | Notes |
| `attachments` | Attach Image | Instrument Photos |
| `customer` | Link (Customer) | Client |
| `accessory_id` | Table (Instrument Accessory) | Accessories & Included Parts |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instrument.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

**Custom Methods:**
- `isn_find_by_serial()`: Custom business logic method
- `autoname()`: Custom business logic method
- `check_duplicate_serial_no()`: Custom business logic method
- `ensure_valid_instrument_category()`: Custom business logic method
- `set_instrument_id()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`instrument.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes
- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Brand** doctype via the `brand` field (Brand)
- Links to **Instrument Category** doctype via the `instrument_category` field (Instrument Category)
- Links to **Customer** doctype via the `customer` field (Client)
- Has child table **Instrument Accessory** stored in the `accessory_id` field

### 5. Critical Files Overview

- **`instrument.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instrument.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`instrument.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_instrument.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
