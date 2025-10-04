## Doctype: Consent Autofill Mapping

### 1. Overview and Purpose

**Consent Autofill Mapping** is a child table doctype used to store related records within a parent document.

**Module:** Customer
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `enabled` | Check | Default: `0` |
| `variable_name` | Data | **Required** |
| `source_doctype` | Link (DocType) | Source DocType |
| `form_link_field` | Data | e.g., 'customer' — must be a field on Consent Form that links to Source DocType |
| `source_fieldname` | Data | Source Fieldname (on Source DocType) |
| `default_value` | Data | Default Value (fallback) |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`consent_autofill_mapping.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

**Custom Methods:**
- `get_mapped_value()`: Custom business logic method
- `test_mapping()`: Custom business logic method
- `get_active_mappings()`: Custom business logic method
- `apply_mappings()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **DocType** doctype via the `source_doctype` field (Source DocType)

### 5. Critical Files Overview

- **`consent_autofill_mapping.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`consent_autofill_mapping.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
