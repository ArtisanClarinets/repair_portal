## Doctype: Consent Template

### 1. Overview and Purpose

**Consent Template** is a doctype in the **Customer** module that manages and tracks related business data.

**Module:** Customer
**Type:** Master/Standard Document

**Description:** Template for legal consent forms used in various processes like sales, repairs, and privacy agreements.

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `title` | Data | **Required**, **Unique** |
| `consent_type` | Select (Sales
Repair
Custom
Privacy
Shipping
Health) | **Required** |
| `version` | Int | **Required**. Default: `1` |
| `content` | Text Editor | **Required**. The full legal text or template content for this consent form. |
| `is_active` | Check | Default: `1` |
| `valid_from` | Date | Valid From |
| `valid_upto` | Date | Valid Upto |
| `required_fields` | Table (Consent Required Field) | Required Fields |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`consent_template.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_update()`**: Runs after document updates

**Custom Methods:**
- `before_cancel()`: Custom business logic method
- `validate_template_syntax()`: Custom business logic method
- `get_available_variables()`: Custom business logic method
- `preview_with_sample_data()`: Custom business logic method
- `duplicate_template()`: Custom business logic method
- `get_usage_statistics()`: Custom business logic method
- `get_template_variables()`: Custom business logic method
- `validate_template_content()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`consent_template.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Has child table **Consent Required Field** stored in the `required_fields` field

### 5. Critical Files Overview

- **`consent_template.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`consent_template.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`consent_template.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
