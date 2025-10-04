## Doctype: Repair Related Document

### 1. Overview and Purpose

**Repair Related Document** is a child table doctype used to store related records within a parent document.

**Module:** Repair
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `doctype_name` | Link (DocType) | **Required** |
| `document_name` | Dynamic Link | **Required** |
| `description` | Small Text | Description |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_related_document.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **DocType** doctype via the `doctype_name` field (Document Type)

### 5. Critical Files Overview

- **`repair_related_document.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_related_document.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
