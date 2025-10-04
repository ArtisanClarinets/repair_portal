## Doctype: Clarinet Setup Log

### 1. Overview and Purpose

**Clarinet Setup Log** is a doctype in the **Instrument Setup** module that manages and tracks related business data.

**Module:** Instrument Setup
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `customer` | Link (Customer) | **Required** |
| `initial_setup` | Link (Clarinet Initial Setup) | **Required** |
| `log_time` | Datetime | Fetched from: `frappe.utils.now_datetime` |
| `instrument_profile` | Link (Instrument Profile) | **Required** |
| `description` | Text | Description |
| `action_by` | Link (User) | Default: `frappe.session.user` |
| `notes` | Text | Notes |
| `attachments` | Attach | Attachments |
| `serial` | Link (Instrument Serial Number) | **Required** |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_setup_log.py`) implements the following:

#### Frontend Logic (JavaScript)

The JavaScript file (`clarinet_setup_log.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Customer** doctype via the `customer` field (Customer)
- Links to **Clarinet Initial Setup** doctype via the `initial_setup` field (Initial Setup)
- Links to **Instrument Profile** doctype via the `instrument_profile` field (Instrument Profile)
- Links to **User** doctype via the `action_by` field (Action By)
- Links to **Instrument Serial Number** doctype via the `serial` field (Serial Number)

### 5. Critical Files Overview

- **`clarinet_setup_log.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_setup_log.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`clarinet_setup_log.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
