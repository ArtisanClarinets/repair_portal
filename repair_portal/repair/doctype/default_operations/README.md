## Doctype: Default Operations

### 1. Overview and Purpose

**Default Operations** is a doctype in the **Repair** module that manages and tracks related business data.

**Module:** Repair
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `operation_type` | Select (
Inventory
Maintenance
Repair) | **Required** |
| `operation_template` | Table (Operation Template) | **Required** |
| `material_used` | Table (Material Use Log) | Material Used |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`default_operations.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`after_insert()`**: Executes after a new document is created
- **`on_update()`**: Runs after document updates
- **`on_trash()`**: Executes before document deletion

**Custom Methods:**
- `before_cancel()`: Custom business logic method
- `after_save()`: Custom business logic method
- `after_rename()`: Custom business logic method
- `onload()`: Custom business logic method
- `get_context()`: Custom business logic method
- `get_operations()`: Custom business logic method
- `get_operations_for_item()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`default_operations.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Has child table **Operation Template** stored in the `operation_template` field
- Has child table **Material Use Log** stored in the `material_used` field

### 5. Critical Files Overview

- **`default_operations.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`default_operations.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`default_operations.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
