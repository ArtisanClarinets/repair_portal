## Doctype: Measurement Session

### 1. Overview and Purpose

**Measurement Session** is a doctype in the **Lab** module that manages and tracks related business data.

**Module:** Lab
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `instrument` | Link (Instrument Profile) | **Required** |
| `technician` | Link (User) | **Required** |
| `date` | Date | Default: `Today` |
| `notes` | Text | Observations, environmental conditions, or session comments. |
| `measurements` | Table (Measurement Entry) | Measurements |
| `workflow_state` | Select (Draft
Awaiting Review
Approved
Archived) | Read-only. Default: `Draft`. Session status: controls lab and QA review visibility. |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`measurement_session.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument Profile** doctype via the `instrument` field (Instrument)
- Links to **User** doctype via the `technician` field (Technician)
- Has child table **Measurement Entry** stored in the `measurements` field

### 5. Critical Files Overview

- **`measurement_session.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`measurement_session.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
