## Doctype: Instrument Model

### 1. Overview and Purpose

**Instrument Model** is a doctype in the **Instrument Profile** module that manages and tracks related business data.

**Module:** Instrument Profile
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `brand` | Link (Brand) | **Required** |
| `model` | Data | **Required** |
| `body_material` | Data | **Required** |
| `instrument_model_id` | Data | **Unique** |
| `instrument_category` | Link (Instrument Category) | **Required** |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instrument_model.py`) implements the following:

#### Frontend Logic (JavaScript)

The JavaScript file (`instrument_model.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes
- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Brand** doctype via the `brand` field (Brand)
- Links to **Instrument Category** doctype via the `instrument_category` field (Instrument Key)

### 5. Critical Files Overview

- **`instrument_model.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instrument_model.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`instrument_model.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_instrument_model.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
