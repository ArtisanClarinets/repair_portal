## Doctype: Related Instrument Interaction

### 1. Overview and Purpose

**Related Instrument Interaction** is a child table doctype used to store related records within a parent document.

**Module:** Repair Logging
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `related_instrument` | Link (Instrument Profile) | Related Instrument |
| `interaction_type` | Select (Follow-up
Referred
Reference) | Interaction Type |
| `notes` | Small Text | Notes |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`related_instrument_interaction.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `get_relationship_history()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument Profile** doctype via the `related_instrument` field (Related Instrument)

### 5. Critical Files Overview

- **`related_instrument_interaction.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`related_instrument_interaction.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
