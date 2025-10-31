## Doctype: Technician

### 1. Overview and Purpose

**Technician** is a doctype in the **Repair Portal** module that manages and tracks related business data.

**Module:** Repair Portal
**Type:** Master/Standard Document

This doctype is used to:

- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `first_name` | Data | **Required** |
| `last_name` | Data | **Required** |
| `user` | Link (User) | **Required** |
| `email` | Data | **Required** |
| `phone` | Data | **Required** |
| `employment_status` | Select (Active
Inactive
Suspended) | **Required**. Default: `Active` |
| `hire_date` | Date | **Required** |
| `notes` | Small Text | Notes |
| `last_active` | Datetime | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`technician.py`) implements the following:

**Lifecycle Hooks:**

- **`before_save()`**: Executes logic before the document is saved
- **`after_insert()`**: Executes after a new document is created
- **`on_update()`**: Runs after document updates

**Custom Methods:**

- `validate_email()`: Custom business logic method
- `validate_phone()`: Custom business logic method
- `send_onboarding_email()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`technician.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes

#### Workflow

This doctype uses a workflow managed by the `employment_status` field to control document states and transitions.

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **User** doctype via the `user` field (User Account)

### 5. Critical Files Overview

- **`technician.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`technician.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`technician.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
