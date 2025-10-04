## Doctype: Loaner Return Check

### 1. Overview and Purpose

**Loaner Return Check** is a doctype in the **Intake** module that manages and tracks related business data.

**Module:** Intake
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `linked_loaner` | Link (Loaner Instrument) | **Required** |
| `condition_notes` | Text | Condition Notes |
| `return_photos` | Attach Image | Photos at Return |
| `damage_found` | Check | Damage Observed |
| `return_date` | Date | Date of Return |
| `workflow_state` | Select (Workflow State) | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`loaner_return_check.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

#### Workflow

This doctype uses a workflow managed by the `workflow_state` field to control document states and transitions.

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Loaner Instrument** doctype via the `linked_loaner` field (Loaner Record)

### 5. Critical Files Overview

- **`loaner_return_check.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`loaner_return_check.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
