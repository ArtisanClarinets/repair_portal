## Doctype: Linked Players

### 1. Overview and Purpose

**Linked Players** is a child table doctype used to store related records within a parent document.

**Module:** Customer
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `customer` | Link (Customer) | **Required** |
| `player_profile` | Link (Player Profile) | **Required** |
| `relationship` | Select (Self
Child
Student
Other) | Relationship to Client |
| `date_linked` | Date | Default: `Today` |
| `is_primary` | Check | Primary Profile? |
| `notes` | Small Text | Notes |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`linked_players.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`on_update()`**: Runs after document updates

**Custom Methods:**
- `before_delete()`: Custom business logic method
- `get_player_details()`: Custom business logic method
- `get_relationship_history()`: Custom business logic method
- `as_dict_safe()`: Custom business logic method
- `get_available_players()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`linked_players.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes
- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Customer** doctype via the `customer` field (Customer)
- Links to **Player Profile** doctype via the `player_profile` field (Player Profile)

### 5. Critical Files Overview

- **`linked_players.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`linked_players.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`linked_players.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
