## Doctype: Repair Portal Settings

### 1. Overview and Purpose

**Repair Portal Settings** is a doctype in the **Repair Portal Settings** module that manages and tracks related business data.

**Module:** Repair Portal Settings
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `repair_portal_settings` | Heading | Repair Portal Settings |
| `standard_hourly_rate` | Currency | Standard Hourly Rate |
| `hours_per_day` | Data | Default: `8` |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_portal_settings.py`) implements the following:

#### Frontend Logic (JavaScript)

The JavaScript file (`repair_portal_settings.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`repair_portal_settings.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_portal_settings.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`repair_portal_settings.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
