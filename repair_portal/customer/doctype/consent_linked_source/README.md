## Doctype: Consent Linked Source

### 1. Overview and Purpose

**Consent Linked Source** is a child table doctype used to store related records within a parent document.

**Module:** Customer
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `enabled` | Check | **Required**. Default: `1` |
| `label` | Data | **Required** |
| `fieldname` | Data | **Required**. e.g., instrument_profile |
| `source_doctype` | Link (DocType) | **Required** |
| `insert_after` | Data | Default: `consent_template`. Fieldname on Consent Form after which this Link will be inserted |
| `reqd` | Check | Default: `0` |
| `read_only` | Check | Default: `0` |
| `hidden` | Check | Default: `0` |
| `in_list_view` | Check | Default: `0` |
| `permlevel` | Int | Default: `0` |
| `depends_on` | Data | Depends On (eval) |
| `description` | Small Text | Description |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`consent_linked_source.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

**Custom Methods:**
- `get_field_definition()`: Custom business logic method
- `get_source_value()`: Custom business logic method
- `test_source()`: Custom business logic method
- `get_active_sources()`: Custom business logic method
- `create_dynamic_fields()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **DocType** doctype via the `source_doctype` field (Source DocType)

### 5. Critical Files Overview

- **`consent_linked_source.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`consent_linked_source.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
