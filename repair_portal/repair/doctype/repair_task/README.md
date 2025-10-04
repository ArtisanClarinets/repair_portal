## Doctype: Repair Task

### 1. Overview and Purpose

**Repair Task** is a doctype in the **Repair** module that manages and tracks related business data.

**Module:** Repair
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `naming_series` | Data | **Required**. Default: `RTASK-.YYYY.-` |
| `repair_order` | Link (Repair Order) | **Required** |
| `task_type` | Link (Activity Type) | Task Type |
| `status` | Select (Open
Running
Completed
On Hold) | Default: `Open` |
| `assigned_to` | Link (User) | Assigned To |
| `est_minutes` | Int | Estimated Minutes |
| `actual_minutes` | Int | Actual Minutes |
| `started_at` | Datetime | Read-only |
| `completed_at` | Datetime | Read-only |
| `notes` | Small Text | Notes |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_task.py`) implements the following:

**Custom Methods:**
- `start()`: Custom business logic method
- `stop()`: Custom business logic method
- `complete()`: Custom business logic method
- `post_task_time()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Repair Order** doctype via the `repair_order` field (Repair Order)
- Links to **Activity Type** doctype via the `task_type` field (Task Type)
- Links to **User** doctype via the `assigned_to` field (Assigned To)

### 5. Critical Files Overview

- **`repair_task.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_task.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
