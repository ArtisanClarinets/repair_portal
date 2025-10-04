## Doctype: Repair Settings

### 1. Overview and Purpose

**Repair Settings** is a doctype in the **Repair Portal Settings** module that manages and tracks related business data.

**Module:** Repair Portal Settings
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `default_company` | Link (Company) | Default Company |
| `default_source_warehouse` | Link (Warehouse) | Default Source Warehouse |
| `default_labor_item` | Link (Item) | Default Labor Item (Service) |
| `default_labor_rate` | Currency | Default Labor Rate |
| `default_qa_required` | Check | Default: `1` |
| `default_require_invoice_before_delivery` | Check | Default: `0` |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_settings.py`) implements the following:

#### Frontend Logic (JavaScript)

The JavaScript file (`repair_settings.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Company** doctype via the `default_company` field (Default Company)
- Links to **Warehouse** doctype via the `default_source_warehouse` field (Default Source Warehouse)
- Links to **Item** doctype via the `default_labor_item` field (Default Labor Item (Service))

### 5. Critical Files Overview

- **`repair_settings.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_settings.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`repair_settings.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
