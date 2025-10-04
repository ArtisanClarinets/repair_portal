## Doctype: Repair Quotation Item

### 1. Overview and Purpose

**Repair Quotation Item** is a child table doctype used to store related records within a parent document.

**Module:** Repair
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `idx` | Int | Idx |
| `item_type` | Select (Labor
Part) | **Required** |
| `item_code` | Link (Item) | Item |
| `description` | Small Text | Description |
| `qty` | Float | Default: `1` |
| `uom` | Link (UOM) | UOM |
| `hours` | Float | Hours (if Labor) |
| `rate` | Currency | **Required** |
| `amount` | Currency | Read-only |
| `technician` | Link (Employee) | Technician |
| `notes` | Data | Notes |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_quotation_item.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Item** doctype via the `item_code` field (Item)
- Links to **UOM** doctype via the `uom` field (UOM)
- Links to **Employee** doctype via the `technician` field (Technician)

### 5. Critical Files Overview

- **`repair_quotation_item.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_quotation_item.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
