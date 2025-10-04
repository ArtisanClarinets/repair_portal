## Doctype: Tool Usage Log

### 1. Overview and Purpose

**Tool Usage Log** is a doctype in the **Repair Logging** module that manages and tracks related business data.

**Module:** Repair Logging
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `tool` | Data | Tool |
| `used_by` | Link (User) | Used By |
| `usage_notes` | Text | Notes |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`tool_usage_log.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `complete_usage()`: Custom business logic method
- `get_tool_usage_history()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **User** doctype via the `used_by` field (Used By)

### 5. Critical Files Overview

- **`tool_usage_log.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`tool_usage_log.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
