## Doctype: Warranty Modification Log

### 1. Overview and Purpose

**Warranty Modification Log** is a child table doctype used to store related records within a parent document.

**Module:** Repair Logging
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `warranty_mod_id` | Data | **Unique**, Read-only |
| `instrument_profile` | Link (Instrument Profile) | **Required** |
| `modified_by` | Link (User) | **Required** |
| `modification_date` | Datetime | **Required**. Default: `Now` |
| `old_start_date` | Date | Old Start Date |
| `new_start_date` | Date | New Start Date |
| `old_end_date` | Date | Old End Date |
| `new_end_date` | Date | New End Date |
| `reason` | Data | **Required** |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`warranty_modification_log.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `get_modification_history()`: Custom business logic method
- `calculate_warranty_timeline()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument Profile** doctype via the `instrument_profile` field (Instrument Profile)
- Links to **User** doctype via the `modified_by` field (Modified By)

### 5. Critical Files Overview

- **`warranty_modification_log.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`warranty_modification_log.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
