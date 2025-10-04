## Doctype: Material Use Log

### 1. Overview and Purpose

**Material Use Log** is a child table doctype used to store related records within a parent document.

**Module:** Repair Logging
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `qty` | Float | **Required**. Default: `1` |
| `used_on` | Data | Used On (Key or Pad) |
| `remarks` | Small Text | Remarks |
| `source_warehouse` | Link (Warehouse) | Source Warehouse |
| `operation_type` | Link (DocType) | Operation Type |
| `operation_link` | Dynamic Link | Operation |
| `item_name` | Link (Item) | **Required** |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`material_use_log.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Warehouse** doctype via the `source_warehouse` field (Source Warehouse)
- Links to **DocType** doctype via the `operation_type` field (Operation Type)
- Links to **Item** doctype via the `item_name` field (Item)

### 5. Critical Files Overview

- **`material_use_log.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`material_use_log.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
