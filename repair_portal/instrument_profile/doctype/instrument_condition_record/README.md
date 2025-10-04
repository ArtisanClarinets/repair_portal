## Doctype: Instrument Condition Record

### 1. Overview and Purpose

**Instrument Condition Record** is a child table doctype used to store related records within a parent document.

**Module:** Instrument Profile
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `instrument` | Link (Instrument) | **Required**, **Unique** |
| `condition` | Select (
New
Good
Fair
Poor
Needs Repair) | **Required** |
| `date_of_record` | Date | **Required** |
| `recorded_by` | Link (User) | Read-only. Default: `__user` |
| `notes` | Text | Notes |
| `workflow_state` | Select (Draft
Recorded
Verified
Archived) | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instrument_condition_record.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

#### Workflow

This doctype uses a workflow managed by the `workflow_state` field to control document states and transitions.

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument** doctype via the `instrument` field (Instrument)
- Links to **User** doctype via the `recorded_by` field (Recorded By)

### 5. Critical Files Overview

- **`instrument_condition_record.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instrument_condition_record.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`test_instrument_condition_record.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
