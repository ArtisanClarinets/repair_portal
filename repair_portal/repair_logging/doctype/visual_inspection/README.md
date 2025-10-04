## Doctype: Visual Inspection

### 1. Overview and Purpose

**Visual Inspection** is a child table doctype used to store related records within a parent document.

**Module:** Repair Logging
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `serial_no` | Link (Serial No) | **Required** |
| `inspection_date` | Date | **Required**. Default: `Today` |
| `inspected_by` | Link (User) | **Required**. Default: `frappe.session.user.full_name` |
| `component` | Select (Body Wood
Tone Holes
Keywork
Pads
Corks
Other) | **Required** |
| `condition` | Data | **Required** |
| `photo` | Attach Image | Photo |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`visual_inspection.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `get_inspection_history()`: Custom business logic method
- `calculate_condition_trends()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Serial No** doctype via the `serial_no` field (Serial Number)
- Links to **User** doctype via the `inspected_by` field (Inspected By)

### 5. Critical Files Overview

- **`visual_inspection.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`visual_inspection.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
