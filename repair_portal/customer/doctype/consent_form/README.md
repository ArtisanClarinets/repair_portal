## Doctype: Consent Form

### 1. Overview and Purpose

**Consent Form** is a submittable doctype in the **Customer** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

**Module:** Customer
**Type:** Submittable Document

This doctype is used to:
- Track business transactions through their lifecycle
- Maintain audit trails with submission and cancellation workflows
- Enforce data integrity through workflow states

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `customer` | Link (Customer) | **Required** |
| `consent_template` | Link (Consent Template) | **Required** |
| `consent_field_values` | Table (Consent Field Value) | Field Values |
| `signature` | Signature | Signature |
| `signed_on` | Datetime | Read-only |
| `rendered_content` | Text Editor | Read-only |
| `status` | Select (Draft
Signed
Cancelled) | Read-only |
| `workflow_state` | Select | Read-only |
| `log_entries` | Table (Consent Log Entry) | Log Entries |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`consent_form.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_insert()`**: Runs before a new document is inserted
- **`after_insert()`**: Executes after a new document is created
- **`on_submit()`**: Executes when the document is submitted
- **`on_cancel()`**: Runs when the document is cancelled

**Custom Methods:**
- `before_submit()`: Custom business logic method
- `refresh_from_template()`: Custom business logic method
- `preview_render()`: Custom business logic method
- `get_available_variables()`: Custom business logic method
- `render_preview()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`consent_form.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Customer** doctype via the `customer` field (Customer)
- Links to **Consent Template** doctype via the `consent_template` field (Consent Template)
- Has child table **Consent Field Value** stored in the `consent_field_values` field
- Has child table **Consent Log Entry** stored in the `log_entries` field

### 5. Critical Files Overview

- **`consent_form.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`consent_form.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`consent_form.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
