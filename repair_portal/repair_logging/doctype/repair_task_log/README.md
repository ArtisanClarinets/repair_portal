## Doctype: Repair Task Log

### 1. Overview and Purpose

**Repair Task Log** is a child table doctype used to store related records within a parent document.

**Module:** Repair Logging
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `log_entry` | Small Text | **Required** |
| `timestamp` | Datetime | Default: `Now` |
| `logged_by` | Link (User) | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_task_log.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `start_task()`: Custom business logic method
- `end_task()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **User** doctype via the `logged_by` field (Logged By)

### 5. Critical Files Overview

- **`repair_task_log.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_task_log.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
