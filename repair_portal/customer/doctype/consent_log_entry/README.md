## Doctype: Consent Log Entry

### 1. Overview and Purpose

**Consent Log Entry** is a child table doctype used to store related records within a parent document.

**Module:** Customer
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `entry_date` | Date | Entry Date |
| `method` | Select (Phone
Text
Email
In Person) | Method |
| `technician` | Link (User) | Technician |
| `notes` | Small Text | Notes |
| `consent_type` | Select (Repair Authorization
Photography
Privacy Waiver) | Consent Type |
| `date_given` | Date | Date Given |
| `reference_doctype` | Link (DocType) | Reference Doctype |
| `reference_name` | Dynamic Link | Reference Name |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`consent_log_entry.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

**Custom Methods:**
- `get_consent_status()`: Custom business logic method
- `get_consent_validity()`: Custom business logic method
- `create_audit_entry()`: Custom business logic method
- `confirm_consent()`: Custom business logic method
- `revoke_consent()`: Custom business logic method
- `get_active_consents()`: Custom business logic method
- `check_consent_coverage()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **User** doctype via the `technician` field (Technician)
- Links to **DocType** doctype via the `reference_doctype` field (Reference Doctype)

### 5. Critical Files Overview

- **`consent_log_entry.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`consent_log_entry.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
