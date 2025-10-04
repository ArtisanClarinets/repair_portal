## Doctype: Clarinet Template Task Depends On

### 1. Overview and Purpose

**Clarinet Template Task Depends On** is a child table doctype used to store related records within a parent document.

**Module:** Instrument Setup
**Type:** Child Table

**Description:** Child table storing template-level task dependencies. Each row references another template task by sequence number that must be completed before the current template task can proceed.

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `sequence` | Int | **Required**. The sequence number of the template task that this task depends on. |
| `subject` | Link (Clarinet Template Task) | **Required**. Task title that this dependency relates to. |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_template_task_depends_on.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Clarinet Template Task** doctype via the `subject` field (Parent Task's Subject)

### 5. Critical Files Overview

- **`clarinet_template_task_depends_on.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_template_task_depends_on.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
