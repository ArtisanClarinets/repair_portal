## Doctype: Consent Field Value

### 1. Overview and Purpose

**Consent Field Value** is a child table doctype used to store related records within a parent document.

**Module:** Customer
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `field_label` | Data | **Required** |
| `field_type` | Select (Data
Int
Date
Float
Small Text
Text
Check
Signature) | **Required** |
| `field_value` | Text | Value |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`consent_field_value.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

**Custom Methods:**
- `get_typed_value()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`consent_field_value.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`consent_field_value.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`consent_field_value.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`consent_field_value.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
