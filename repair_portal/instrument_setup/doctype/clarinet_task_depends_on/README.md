## Doctype: Clarinet Task Depends On

### 1. Overview and Purpose

**Clarinet Task Depends On** is a child table doctype used to store related records within a parent document.

**Module:** Instrument Setup
**Type:** Child Table

**Description:** Child table storing predecessor tasks (dependencies) for a Clarinet Setup Task. Each row links to another task that must be Completed before the current task can proceed.

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `task` | Link (Clarinet Setup Task) | **Required**. The prerequisite Clarinet Setup Task that this task depends on. |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_task_depends_on.py`) implements the following:

#### Frontend Logic (JavaScript)

The JavaScript file (`clarinet_task_depends_on.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Clarinet Setup Task** doctype via the `task` field (Task)

### 5. Critical Files Overview

- **`clarinet_task_depends_on.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_task_depends_on.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`clarinet_task_depends_on.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
