## Doctype: Service Task

### 1. Overview and Purpose

**Service Task** is a doctype in the **Service Planning** module that manages and tracks related business data.

**Module:** Service Planning
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `task_name` | Data | **Required** |
| `description` | Text | Description |
| `scheduled_date` | Date | Scheduled Date |
| `assigned_to` | Link (User) | Assigned To |
| `workflow_state` | Select (Workflow State) | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`service_task.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **User** doctype via the `assigned_to` field (Assigned To)

### 5. Critical Files Overview

- **`service_task.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`service_task.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
