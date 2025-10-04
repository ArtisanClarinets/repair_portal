## Doctype: Repair Estimate

### 1. Overview and Purpose

**Repair Estimate** is a doctype in the **Service Planning** module that manages and tracks related business data.

**Module:** Service Planning
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `customer_name` | Data | **Required** |
| `instrument_id` | Data | Instrument ID |
| `inspection_reference` | Link (Inspection Report) | Inspection Reference |
| `estimated_completion` | Date | Estimated Completion |
| `line_items` | Table (Estimate Line Item) | Line Items |
| `total_cost` | Currency | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_estimate.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Inspection Report** doctype via the `inspection_reference` field (Inspection Reference)
- Has child table **Estimate Line Item** stored in the `line_items` field

### 5. Critical Files Overview

- **`repair_estimate.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_estimate.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
