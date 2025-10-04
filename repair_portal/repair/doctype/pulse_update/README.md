## Doctype: Pulse Update

### 1. Overview and Purpose

**Pulse Update** is a doctype in the **Repair** module that manages and tracks related business data.

**Module:** Repair
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `repair_order` | Link (Repair Order) | **Required** |
| `update_time` | Datetime | **Required**. Default: `now` |
| `status` | Select (Draft
Inspection
Planning
In Progress
Delayed
QA
Ready for Pickup
Completed
Closed) | Status |
| `update_note` | Small Text | Update Note |
| `percent_complete` | Int | Percent Complete |
| `entered_by` | Link (User) | Entered By |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`pulse_update.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Repair Order** doctype via the `repair_order` field (Repair Order)
- Links to **User** doctype via the `entered_by` field (Entered By)

### 5. Critical Files Overview

- **`pulse_update.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`pulse_update.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
