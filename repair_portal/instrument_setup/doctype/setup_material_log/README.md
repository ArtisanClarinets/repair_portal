## Doctype: Setup Material Log

### 1. Overview and Purpose

**Setup Material Log** is a child table doctype used to store related records within a parent document.

**Module:** Instrument Setup
**Type:** Child Table

**Description:** Child table used to record materials consumed during clarinet setup/repair. Each row captures item, quantity, unit, rate, and extended amount for costing and documentation.

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `item_code` | Link (Item) | **Required**. Stock Item used (e.g., pad, cork, spring). |
| `description` | Small Text | Optional item description shown on the certificate or internal reports. |
| `qty` | Float | Default: `1`. Quantity consumed. |
| `uom` | Link (UOM) | Unit of Measure for the quantity (e.g., pcs, set, cm). |
| `rate` | Currency | Unit cost used for extended amount calculation. |
| `amount` | Currency | Read-only. Extended line amount (qty × rate). Kept read-only; computed server-side and mirrored client-side. |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`setup_material_log.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

#### Frontend Logic (JavaScript)

The JavaScript file (`setup_material_log.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Item** doctype via the `item_code` field (Item)
- Links to **UOM** doctype via the `uom` field (UOM)

### 5. Critical Files Overview

- **`setup_material_log.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`setup_material_log.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`setup_material_log.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
