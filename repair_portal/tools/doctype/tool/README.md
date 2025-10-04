## Doctype: Tool

### 1. Overview and Purpose

**Tool** is a doctype in the **Tools** module that manages and tracks related business data.

**Module:** Tools
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `tool_name` | Data | **Required** |
| `tool_type` | Select (Lathe
Drill Press
Screwdriver
Pliers
Reamer
Drill Bit
Other) | Tool Type |
| `location` | Data | Location |
| `in_service` | Check | Default: `1` |
| `requires_calibration` | Check | Check if this tool requires periodic calibration. |
| `last_calibrated` | Date | Date of the most recent calibration. |
| `next_due` | Date | Date when the next calibration is required for compliance. |
| `asset` | Link (Asset) | ERPNext Asset record for this tool (if tracked financially). |
| `notes` | Small Text | Notes |
| `workflow_state` | Select (Available
Out for Calibration
Retired) | Read-only. Current lifecycle state of the tool. Managed by workflow automation. |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`tool.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `send_calibration_due_notifications()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Asset** doctype via the `asset` field (ERPNext Asset)

### 5. Critical Files Overview

- **`tool.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`tool.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
