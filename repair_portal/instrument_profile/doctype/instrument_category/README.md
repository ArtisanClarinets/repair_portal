## Doctype: Instrument Category

### 1. Overview and Purpose

**Instrument Category** is a doctype in the **Instrument Profile** module that manages and tracks related business data.

**Module:** Instrument Profile
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `title` | Data | **Required**, **Unique** |
| `description` | Small Text | Description |
| `is_active` | Check | Default: `1` |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instrument_category.py`) implements the following:

#### Frontend Logic (JavaScript)

The JavaScript file (`instrument_category.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes
- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`instrument_category.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instrument_category.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`instrument_category.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_instrument_category.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
