## Doctype: Repair Actual Material

### 1. Overview and Purpose

**Repair Actual Material** is a child table doctype used to store related records within a parent document.

**Module:** Repair
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `item_code` | Link (Item) | **Required** |
| `description` | Small Text | Description |
| `qty` | Float | **Required**. Default: `1` |
| `uom` | Link (UOM) | Default: `Nos` |
| `valuation_rate` | Currency | Read-only |
| `amount` | Currency | Read-only |
| `stock_entry` | Link (Stock Entry) | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_actual_material.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

#### Frontend Logic (JavaScript)

The JavaScript file (`repair_actual_material.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Item** doctype via the `item_code` field (Item)
- Links to **UOM** doctype via the `uom` field (UOM)
- Links to **Stock Entry** doctype via the `stock_entry` field (Stock Entry)

### 5. Critical Files Overview

- **`repair_actual_material.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_actual_material.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`repair_actual_material.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
