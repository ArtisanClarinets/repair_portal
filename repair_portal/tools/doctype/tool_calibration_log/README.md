## Doctype: Tool Calibration Log

### 1. Overview and Purpose

**Tool Calibration Log** is a doctype in the **Tools** module that manages and tracks related business data.

**Module:** Tools
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `tool_name` | Data | Tool Name |
| `calibration_date` | Date | Calibration Date |
| `calibrated_by` | Link (Technician) | Calibrated By |
| `next_due` | Date | Next Calibration Due |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`tool_calibration_log.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Technician** doctype via the `calibrated_by` field (Calibrated By)

### 5. Critical Files Overview

- **`tool_calibration_log.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`tool_calibration_log.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
