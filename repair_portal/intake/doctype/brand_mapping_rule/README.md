## Doctype: Brand Mapping Rule

### 1. Overview and Purpose

**Brand Mapping Rule** is a child table doctype used to store related records within a parent document.

**Module:** Intake
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `from_brand` | Data | **Required** |
| `to_brand` | Data | **Required** |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`brand_mapping_rule.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

**Custom Methods:**
- `map_brand()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`brand_mapping_rule.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`brand_mapping_rule.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`test_brand_mapping_rule.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
