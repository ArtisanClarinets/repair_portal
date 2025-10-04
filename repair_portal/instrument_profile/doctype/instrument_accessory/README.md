## Doctype: Instrument Accessory

### 1. Overview and Purpose

**Instrument Accessory** is a child table doctype used to store related records within a parent document.

**Module:** Instrument Profile
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `accessory_id` | Data | **Unique**, Read-only |
| `accessory` | Data | **Required** |
| `desc` | Text | **Required** |
| `serial_no` | Data | Serial/ID |
| `acquired_date` | Date | **Required** |
| `removed_date` | Date | Removed Date |
| `current` | Check | Default: `1` |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instrument_accessory.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`instrument_accessory.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instrument_accessory.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`test_instrument_accessory.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
