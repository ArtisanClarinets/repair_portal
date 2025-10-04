## Doctype: Service Plan

### 1. Overview and Purpose

**Service Plan** is a doctype in the **Service Planning** module that manages and tracks related business data.

**Module:** Service Planning
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `plan_date` | Date | Plan Date |
| `instrument` | Link (Instrument Profile) | Instrument |
| `estimated_cost` | Currency | Estimated Cost |
| `labor_hours` | Float | Labor Hours |
| `notes` | Small Text | Planning notes or special instructions for this service plan. |
| `tasks` | Table (Repair Task Log) | Planned Tasks |
| `plan_status` | Select (Draft
Scheduled
In Progress
Completed
Archived) | Read-only. Default: `Draft`. Current workflow state of this service plan. Managed by workflow automation. |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`service_plan.py`) implements the following:

**Lifecycle Hooks:**
- **`on_submit()`**: Executes when the document is submitted

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument Profile** doctype via the `instrument` field (Instrument)
- Has child table **Repair Task Log** stored in the `tasks` field

### 5. Critical Files Overview

- **`service_plan.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`service_plan.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
