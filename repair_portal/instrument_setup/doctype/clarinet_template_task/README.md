## Doctype: Clarinet Template Task

### 1. Overview and Purpose

**Clarinet Template Task** is a child table doctype used to store related records within a parent document.

**Module:** Instrument Setup
**Type:** Child Table

**Description:** Child table that defines task templates within a Setup Template. Each row generates a real Clarinet Setup Task with expected schedule and priority when applied to a Clarinet Initial Setup.

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `sequence` | Int | **Required**. Ordering number used when generating tasks (e.g., 10, 20, 30). |
| `depends_on` | Table (Clarinet Template Task Depends On) | Template-level predecessors (referencing other template rows by sequence). |
| `subject` | Data | **Required**. Task title that will be copied to the generated Clarinet Setup Task. |
| `description` | Small Text | Optional notes that will be copied to the generated Clarinet Setup Task. |
| `default_priority` | Select (Low
Medium
High
Urgent) | Default: `Medium`. Priority to apply to the generated task. |
| `exp_start_offset_days` | Int | Default: `0`. Days after the Setup Date that the generated task should start (0 = same day). |
| `exp_duration_mins` | Int | Default: `1`. Planned duration in days for the generated task (at least 1). |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_template_task.py`) implements the following:

#### Frontend Logic (JavaScript)

The JavaScript file (`clarinet_template_task.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Has child table **Clarinet Template Task Depends On** stored in the `depends_on` field

### 5. Critical Files Overview

- **`clarinet_template_task.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_template_task.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`clarinet_template_task.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
