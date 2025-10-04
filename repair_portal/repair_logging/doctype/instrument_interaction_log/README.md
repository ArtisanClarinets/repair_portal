## Doctype: Instrument Interaction Log

### 1. Overview and Purpose

**Instrument Interaction Log** is a child table doctype used to store related records within a parent document.

**Module:** Repair Logging
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `interaction_type` | Select (Intake
Inspection
Repair
QA
Upgrade) | Interaction Type |
| `reference_doctype` | Data | Reference DocType |
| `reference_name` | Dynamic Link | Reference Name |
| `date` | Date | Date |
| `notes` | Small Text | Notes |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instrument_interaction_log.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `add_follow_up_note()`: Custom business logic method
- `get_interaction_history()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`instrument_interaction_log.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instrument_interaction_log.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
