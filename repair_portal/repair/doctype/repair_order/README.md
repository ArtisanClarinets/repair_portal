## Doctype: Repair Order

### 1. Overview and Purpose

**Repair Order** is a doctype in the **Repair** module that manages and tracks related business data.

**Module:** Repair
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `naming_series` | Data | **Required**. Default: `RO-.YYYY.-` |
| `customer` | Link (Customer) | **Required** |
| `instrument_profile` | Link (Instrument Profile) | Instrument Profile |
| `company` | Link (Company) | Company |
| `posting_date` | Date | Default: `Today` |
| `priority` | Select (Low
Medium
High
Critical) | Default: `Medium` |
| `assigned_technician` | Link (User) | Assigned Technician |
| `target_delivery` | Date | Target Delivery |
| `planned_materials` | Table (Repair Planned Material) | Planned Materials |
| `warehouse_source` | Link (Warehouse) | **Required** |
| `actual_materials` | Table (Repair Actual Material) | Actual Materials |
| `labor_item` | Link (Item) | **Required** |
| `labor_rate` | Currency | Default: `0` |
| `total_estimated_minutes` | Int | Read-only |
| `total_actual_minutes` | Int | Read-only |
| `qa_required` | Check | Default: `1` |
| `require_invoice_before_delivery` | Check | Default: `0` |
| `workflow_state` | Select (Draft
In Progress
QA
Ready
Delivered
Closed) | Read-only. Default: `Draft` |
| `remarks` | Small Text | Remarks |
| `related_documents` | Table (Repair Related Document) | Related Documents |
| ... | ... | *3 more fields* |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_order.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

**Custom Methods:**
- `opt()`: Custom business logic method
- `create_child()`: Custom business logic method
- `create_material_issue_draft()`: Custom business logic method
- `refresh_actuals_from_stock_entry()`: Custom business logic method
- `generate_sales_invoice_from_ro()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`repair_order.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Customer** doctype via the `customer` field (Customer)
- Links to **Instrument Profile** doctype via the `instrument_profile` field (Instrument Profile)
- Links to **Company** doctype via the `company` field (Company)
- Links to **User** doctype via the `assigned_technician` field (Assigned Technician)
- Has child table **Repair Planned Material** stored in the `planned_materials` field
- Links to **Warehouse** doctype via the `warehouse_source` field (Source Warehouse)
- Has child table **Repair Actual Material** stored in the `actual_materials` field
- Links to **Item** doctype via the `labor_item` field (Labor Item (Service))
- Has child table **Repair Related Document** stored in the `related_documents` field
- Links to **Clarinet Intake** doctype via the `intake` field (Intake)

### 5. Critical Files Overview

- **`repair_order.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_order.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`repair_order.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_repair_order.py`**: Unit tests for validating doctype functionality
- **`repair_order_list.js`**: Custom list view behavior and interactions

---

*Last updated: 2025-10-04*
