## Doctype: Repair Parts Used

### 1. Overview and Purpose

**Repair Parts Used** is a child table doctype used to store related records within a parent document.

**Module:** Repair Logging
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `item_code` | Link (Item) | **Required** |
| `item_name` | Data | Fetched from: `item_code.item_name` |
| `qty` | Float | **Required** |
| `uom` | Link (UOM) | Fetched from: `item_code.stock_uom` |
| `rate` | Currency | Rate |
| `amount` | Currency | Read-only |
| `warehouse` | Link (Warehouse) | Warehouse |
| `serial_no` | Link (Serial No) | Serial No |
| `used_on` | Date | Default: `Today` |
| `location` | Data | Location |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_parts_used.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `validate_inventory_availability()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Item** doctype via the `item_code` field (Item Code)
- Links to **UOM** doctype via the `uom` field (UOM)
- Links to **Warehouse** doctype via the `warehouse` field (Warehouse)
- Links to **Serial No** doctype via the `serial_no` field (Serial No)

### 5. Critical Files Overview

- **`repair_parts_used.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_parts_used.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
