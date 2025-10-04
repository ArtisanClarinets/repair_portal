## Doctype: Clarinet Pad Map

### 1. Overview and Purpose

**Clarinet Pad Map** is a doctype in the **Instrument Setup** module that manages and tracks related business data.

**Module:** Instrument Setup
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `clarinet_model` | Link (Instrument Model) | Clarinet Model |
| `top_joint_pads` | Table (Clarinet Pad Entry) | Top Joint Pads |
| `bottom_joint_pads` | Table (Clarinet Pad Entry) | Bottom Joint Pads |
| `instrument_category` | Link (Instrument Category) | Fetched from: `clarinet_model.instrument_category` |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_pad_map.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

**Custom Methods:**
- `get_clarinet_type()`: Custom business logic method
- `populate_standard_pad_names()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`clarinet_pad_map.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument Model** doctype via the `clarinet_model` field (Clarinet Model)
- Has child table **Clarinet Pad Entry** stored in the `top_joint_pads` field
- Has child table **Clarinet Pad Entry** stored in the `bottom_joint_pads` field
- Links to **Instrument Category** doctype via the `instrument_category` field (Instrument Key )

### 5. Critical Files Overview

- **`clarinet_pad_map.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_pad_map.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`clarinet_pad_map.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
