## Doctype: Customer External Work Log

### 1. Overview and Purpose

**Customer External Work Log** is a child table doctype used to store related records within a parent document.

**Module:** Instrument Profile
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `service_date` | Date | **Required** |
| `service_type` | Select (Inspection
Setup
Maintenance
Repair
Other) | Type of Service |
| `service_notes` | Text | Description / Notes |
| `external_shop_name` | Data | Performed By (Shop Name) |
| `receipt_attachment` | Attach | Receipt / Proof of Service |
| `instrument` | Link (Instrument) | **Required** |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`customer_external_work_log.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_insert()`**: Runs before a new document is inserted
- **`after_insert()`**: Executes after a new document is created

#### Frontend Logic (JavaScript)

The JavaScript file (`customer_external_work_log.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes
- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument** doctype via the `instrument` field (Instrument)

### 5. Critical Files Overview

- **`customer_external_work_log.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`customer_external_work_log.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`customer_external_work_log.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_customer_external_work_log.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
