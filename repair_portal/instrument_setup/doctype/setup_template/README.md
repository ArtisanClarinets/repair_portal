## Doctype: Setup Template

### 1. Overview and Purpose

**Setup Template** is a doctype in the **Instrument Setup** module that manages and tracks related business data.

**Module:** Instrument Setup
**Type:** Master/Standard Document

**Description:** Defines reusable defaults for clarinet setup: operations, checklist items, and a list of template tasks. When applied to a Clarinet Initial Setup, this template can populate operations, checklist, and generate scheduled tasks.

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `template_name` | Data | **Required**, **Unique**. Internal identifier for this template (kept unique and set only once). |
| `clarinet_model` | Link (Instrument Model) | **Required**. Model this template is designed for (used for pad maps and model-specific defaults). |
| `setup_type` | Select (Standard Setup
Advanced Setup
Repair & Setup
Maintenance
Overhaul
Custom Setup) | **Required**. Type of setup work this template is designed for. |
| `is_active` | Check | Default: `1`. Whether this template is active and available for use. |
| `priority` | Select (Low
Medium
High
Urgent) | Default: `Medium`. Default priority level for setups created from this template. |
| `pad_map` | Link (Clarinet Pad Map) | Associated pad map record for reference while performing the setup. |
| `estimated_hours` | Float | Estimated labor hours required for this setup type. |
| `estimated_cost` | Currency | Estimated total cost including labor and materials. |
| `estimated_materials_cost` | Currency | Estimated materials cost for this setup type. |
| `default_technician` | Link (User) | Default technician for setups using this template. |
| `default_operations` | Table (Clarinet Setup Operation) | Operations to pre-populate into Clarinet Initial Setup → Operations Performed. Each row describes a standard operation you routinely perform. |
| `checklist_items` | Table (Setup Checklist Item) | Checklist rows to pre-populate into Clarinet Initial Setup → Checklist (e.g., safety check, leak test). |
| `template_tasks` | Table (Clarinet Template Task) | Task blueprints that generate real Clarinet Setup Tasks (with offsets/durations) when applied on a Clarinet Initial Setup. |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`setup_template.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

**Custom Methods:**
- `validate_template_consistency()`: Custom business logic method
- `auto_create_pad_map()`: Custom business logic method
- `validate_template_tasks()`: Custom business logic method
- `recalc()`: Custom business logic method
- `get_template_summary()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`setup_template.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument Model** doctype via the `clarinet_model` field (Instrument Model)
- Links to **Clarinet Pad Map** doctype via the `pad_map` field (Pad Map)
- Links to **User** doctype via the `default_technician` field (Default Technician)
- Has child table **Clarinet Setup Operation** stored in the `default_operations` field
- Has child table **Setup Checklist Item** stored in the `checklist_items` field
- Has child table **Clarinet Template Task** stored in the `template_tasks` field

### 5. Critical Files Overview

- **`setup_template.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`setup_template.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`setup_template.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
