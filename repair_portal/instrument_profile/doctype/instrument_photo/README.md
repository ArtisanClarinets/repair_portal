## Doctype: Instrument Photo

### 1. Overview and Purpose

**Instrument Photo** is a child table doctype used to store related records within a parent document.

**Module:** Instrument Profile
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `photo` | Attach Image | **Required** |
| `category` | Select (Profile Picture
Service Before
Service After
Damage Documentation
Repair Documentation
Other) | **Required** |
| `description` | Data | Description |
| `timestamp` | Datetime | Photo Timestamp |
| `uploaded_by` | Link (User) | **Required** |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instrument_photo.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **User** doctype via the `uploaded_by` field (Uploaded By)

### 5. Critical Files Overview

- **`instrument_photo.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instrument_photo.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`test_instrument_photo.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
