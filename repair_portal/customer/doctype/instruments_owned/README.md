## Doctype: Instruments Owned

### 1. Overview and Purpose

**Instruments Owned** is a child table doctype used to store related records within a parent document.

**Module:** Customer
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `instrument_category` | Data | Instrument Category |
| `serial_no` | Link (Serial No) | Serial Number |
| `customer` | Link (Customer) | **Required** |
| `instrument_profile` | Link (Instrument Profile) | **Required** |
| `purchase_date` | Date | Purchase Date |
| `condition` | Select (
New
Good
Fair
Poor) | Condition |
| `notes` | Small Text | Notes |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instruments_owned.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`on_update()`**: Runs after document updates

**Custom Methods:**
- `before_delete()`: Custom business logic method
- `get_ownership_history()`: Custom business logic method
- `check_warranty_status()`: Custom business logic method
- `get_service_history()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Serial No** doctype via the `serial_no` field (Serial Number)
- Links to **Customer** doctype via the `customer` field (Customer)
- Links to **Instrument Profile** doctype via the `instrument_profile` field (Instrument Profile)

### 5. Critical Files Overview

- **`instruments_owned.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instruments_owned.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
