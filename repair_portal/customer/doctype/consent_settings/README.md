## Doctype: Consent Settings

### 1. Overview and Purpose

**Consent Settings** is a doctype in the **Customer** module that manages and tracks related business data.

**Module:** Customer
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `enable_auto_fill` | Check | Default: `1` |
| `apply_on_save` | Check | Default: `1` |
| `mappings` | Table (Consent Autofill Mapping) | Mappings |
| `linked_sources` | Table (Consent Linked Source) | Linked Sources |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`consent_settings.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`after_insert()`**: Executes after a new document is created
- **`on_update()`**: Runs after document updates

**Custom Methods:**
- `apply_linked_sources()`: Custom business logic method
- `create_default_templates()`: Custom business logic method
- `ensure_workflow()`: Custom business logic method
- `get_available_variables()`: Custom business logic method
- `validate_template_syntax()`: Custom business logic method
- `get_consent_settings()`: Custom business logic method
- `validate_field_mapping()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`consent_settings.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Has child table **Consent Autofill Mapping** stored in the `mappings` field
- Has child table **Consent Linked Source** stored in the `linked_sources` field

### 5. Critical Files Overview

- **`consent_settings.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`consent_settings.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`consent_settings.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
