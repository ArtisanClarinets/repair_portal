## Doctype: Tone Hole Inspection Record

### 1. Overview and Purpose

**Tone Hole Inspection Record** is a child table doctype used to store related records within a parent document.

**Module:** Repair Logging
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `tone_hole_number` | Int | Tone Hole Number |
| `visual_status` | Select (Clean
Damaged
Chipped
Uneven) | Visual Status |
| `notes` | Small Text | Notes |
| `photo` | Attach Image | Photo |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`tone_hole_inspection_record.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

#### Frontend Logic (JavaScript)

The JavaScript file (`tone_hole_inspection_record.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

*This doctype has no explicit relationships with other doctypes through Link or Table fields.*

### 5. Critical Files Overview

- **`tone_hole_inspection_record.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`tone_hole_inspection_record.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`tone_hole_inspection_record.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
