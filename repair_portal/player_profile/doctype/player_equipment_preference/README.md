## Doctype: Player Equipment Preference

### 1. Overview and Purpose

**Player Equipment Preference** is a child table doctype used to store related records within a parent document.

**Module:** Player Profile
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `mouthpiece` | Data | Mouthpiece |
| `ligature` | Data | Ligature |
| `reed_brand` | Data | Reed Brand |
| `reed_model` | Data | Reed Model |
| `reed_strength` | Data | Reed Strength |
| `barrel` | Data | Barrel |
| `instrument` | Link (Instrument Profile) | Instrument |
| `comments` | Small Text | Comments |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`player_equipment_preference.py`) implements the following:

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument Profile** doctype via the `instrument` field (Instrument)

### 5. Critical Files Overview

- **`player_equipment_preference.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`player_equipment_preference.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`test_player_equipment_preference.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
