## Doctype: Customer Type

### 1. Overview and Purpose

**Customer Type** is a doctype in the **Customer** module that manages and tracks related business data.

**Module:** Customer
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `naming_series` | Data | Read-only. Default: `CPT-` |
| `type_name` | Data | **Required**, **Unique** |
| `is_default` | Check | Default |
| `portal_visible` | Check | Default: `1` |
| `description` | Small Text | Description |
| `color` | Color | Color |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`customer_type.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`on_update()`**: Runs after document updates

**Custom Methods:**
- `before_delete()`: Custom business logic method
- `get_customer_count()`: Custom business logic method
- `get_customer_list()`: Custom business logic method
- `get_default_customer_type()`: Custom business logic method
- `get_active_customer_types()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`customer_type.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`customer_type.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
