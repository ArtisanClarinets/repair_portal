## Doctype: Clarinet Setup Operation

### 1. Overview and Purpose

**Clarinet Setup Operation** is a child table doctype used to store related records within a parent document.

**Module:** Instrument Setup
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `operation_type` | Select (Tone Hole Reaming
Tone Hole Repair
Chimney Leak
Tenon Fitting
Key Height Adjustment
Spring Tension Adjustment
Pad Leveling
Cork Replacement
Setup
Other) | Operation Type |
| `section` | Select (All
Mouthpiece
Barrel
Upper Joint
Lower Joint
Bell) | Section |
| `component_ref` | Data | Component Ref (Tone Hole, Key, etc.) |
| `details` | Text | Details / Notes |
| `completed` | Check | Default: `0` |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_setup_operation.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`clarinet_setup_operation.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_setup_operation.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
