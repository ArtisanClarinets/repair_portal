## Doctype: Intake Accessory Item

### 1. Overview and Purpose

**Intake Accessory Item** is a child table doctype used to store related records within a parent document.

**Module:** Intake
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `item_code` | Link (Item) | **Required** |
| `description` | Small Text | Fetched from: `item_code.description` |
| `qty` | Float | **Required**. Default: `1` |
| `uom` | Link (UOM) | Fetched from: `item_code.stock_uom` |
| `rate` | Currency | Rate |
| `amount` | Currency | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`intake_accessory_item.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Item** doctype via the `item_code` field (Item)
- Links to **UOM** doctype via the `uom` field (UOM)

### 5. Critical Files Overview

- **`intake_accessory_item.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`intake_accessory_item.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
