## Doctype: Tenon Measurement

### 1. Overview and Purpose

**Tenon Measurement** is a child table doctype used to store related records within a parent document.

**Module:** Repair Logging
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `measurement_type` | Select (tenon
socket
fit) | **Required** |
| `tenon_type` | Select (Mouthpiece
Upper Joint: Top
Upper Joint: Bottom
Lower Joint: Bottom) | **Required** |
| `tenon_height` | Float | Tenon Height (mm) |
| `tenon_external_diameter` | Float | Tenon External Diameter (mm) |
| `tenon_internal_diameter` | Float | Tenon Internal Diameter (mm) |
| `tenon_wall_thickness` | Float | Tenon Wall Thickness (mm) |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`tenon_measurement.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `get_measurement_history()`: Custom business logic method
- `calculate_fit_analysis()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`tenon_measurement.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`tenon_measurement.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
