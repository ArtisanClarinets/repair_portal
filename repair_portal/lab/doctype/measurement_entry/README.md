## Doctype: Measurement Entry

### 1. Overview and Purpose

**Measurement Entry** is a child table doctype used to store related records within a parent document.

**Module:** Lab
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `parameter` | Data | **Required** |
| `value` | Float | **Required** |
| `unit` | Data | Unit |
| `comments` | Small Text | Comments |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`measurement_entry.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`measurement_entry.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`measurement_entry.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
