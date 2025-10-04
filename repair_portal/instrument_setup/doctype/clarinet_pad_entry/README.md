## Doctype: Clarinet Pad Entry

### 1. Overview and Purpose

**Clarinet Pad Entry** is a child table doctype used to store related records within a parent document.

**Module:** Instrument Setup
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `pad_position` | Data | Pad Position |
| `is_secondary_pad` | Check | Default: `0`. Is this a secondary pad? (Secondary pads are the pads that are controlled by anything but the players finger. E.g. The LH2 is a secondary key when the RH1 is pressed for 1-and-1 |
| `parent_pad` | Link (Clarinet Pad Entry) | Parent Pad |
| `pad_type` | Data | Please only input the type of material of the pad. (E.g. Leather, Cork, Double-Skin, GoreTex, etc.) |
| `is_open_key` | Check | Default: `0` |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_pad_entry.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Clarinet Pad Entry** doctype via the `parent_pad` field (Parent Pad)

### 5. Critical Files Overview

- **`clarinet_pad_entry.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_pad_entry.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
