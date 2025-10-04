## Doctype: Estimate Line Item

### 1. Overview and Purpose

**Estimate Line Item** is a child table doctype used to store related records within a parent document.

**Module:** Service Planning
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `description` | Data | **Required** |
| `part_code` | Link (Item) | Part Code |
| `hours` | Float | Hours |
| `rate` | Currency | Rate ($/hr) |
| `amount` | Currency | Amount |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`estimate_line_item.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Item** doctype via the `part_code` field (Part Code)

### 5. Critical Files Overview

- **`estimate_line_item.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`estimate_line_item.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
