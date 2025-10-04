## Doctype: Diagnostic Metrics

### 1. Overview and Purpose

**Diagnostic Metrics** is a child table doctype used to store related records within a parent document.

**Module:** Repair Logging
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `metric` | Select (Leak Test (Magnehelic)
Endoscopic Finding
Key Clearance
Spring Tension
Acoustic Baseline) | Metric |
| `value` | Data | Value |
| `unit` | Data | Unit |
| `benchmark` | Data | Benchmark / Target |
| `notes` | Data | Notes |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`diagnostic_metrics.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `is_out_of_range()`: Custom business logic method
- `recalculate_metrics()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`diagnostic_metrics.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`diagnostic_metrics.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
