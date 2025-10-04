## Doctype: Clarinet Initial Setup

### 1. Overview and Purpose

**Clarinet Initial Setup** is a submittable doctype in the **Instrument Setup** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

**Module:** Instrument Setup
**Type:** Submittable Document

This doctype is used to:
- Track business transactions through their lifecycle
- Maintain audit trails with submission and cancellation workflows
- Enforce data integrity through workflow states

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `status` | Select (Open
In Progress
Completed
On Hold
Cancelled
QA Review
Customer Approval) | Default: `Open`. Current status of this setup project. |
| `priority` | Select (Low
Medium
High
Urgent) | Default: `Medium`. Priority level for this setup project. |
| `setup_type` | Select (Standard Setup
Advanced Setup
Repair & Setup
Custom Setup) | Default: `Standard Setup`. Type of setup work being performed. |
| `expected_start_date` | Date | Expected start date for this setup project. |
| `expected_end_date` | Date | Expected completion date for this setup project. |
| `actual_start_date` | Datetime | Read-only. Actual date when setup work started. |
| `actual_end_date` | Datetime | Read-only. Actual date when setup work was completed. |
| `progress` | Percent | Read-only |
| `serial` | Link (Instrument Serial Number) | Fetched from: `instrument.serial_no` |
| `instrument` | Link (Instrument) | **Required** |
| `instrument_profile` | Link (Instrument Profile) | Read-only |
| `clarinet_type` | Select (B♭ Clarinet
A Clarinet
E♭ Clarinet
Bass Clarinet
Alto Clarinet
Contrabass Clarinet
Other) | Type of Clarinet |
| `model` | Data | Read-only. Fetched from: `instrument.model` |
| `intake` | Link (Clarinet Intake) | Intake |
| `inspection` | Link (Instrument Inspection) | Read-only. Fetched from: `instrument_profile.linked_inspection` |
| `technician` | Link (User) | Technician |
| `setup_date` | Date | Setup Date |
| `labor_hours` | Float | Labor Hours |
| `estimated_cost` | Currency | Read-only. Estimated total cost for this setup project. |
| `actual_cost` | Currency | Read-only. Actual total cost incurred for this setup project. |
| ... | ... | *11 more fields* |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_initial_setup.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `on_update_after_submit()`: Custom business logic method
- `set_defaults_from_template()`: Custom business logic method
- `set_project_dates()`: Custom business logic method
- `validate_project_dates()`: Custom business logic method
- `update_actual_dates()`: Custom business logic method
- `calculate_costs()`: Custom business logic method
- `ensure_checklist()`: Custom business logic method
- `load_operations_from_template()`: Custom business logic method
- `create_tasks_from_template()`: Custom business logic method
- `generate_certificate()`: Custom business logic method
- *...and 1 more methods*

#### Frontend Logic (JavaScript)

The JavaScript file (`clarinet_initial_setup.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes
- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument Serial Number** doctype via the `serial` field (Serial No)
- Links to **Instrument** doctype via the `instrument` field (Instrument)
- Links to **Instrument Profile** doctype via the `instrument_profile` field (Instrument Profile)
- Links to **Clarinet Intake** doctype via the `intake` field (Intake)
- Links to **Instrument Inspection** doctype via the `inspection` field (Inspection)
- Links to **User** doctype via the `technician` field (Technician)
- Links to **Setup Template** doctype via the `setup_template` field (Setup Template)
- Has child table **Setup Checklist Item** stored in the `checklist` field
- Has child table **Clarinet Setup Operation** stored in the `operations_performed` field
- Has child table **Setup Material Log** stored in the `materials_used` field
- Has child table **Instrument Interaction Log** stored in the `notes` field
- Links to **Clarinet Initial Setup** doctype via the `amended_from` field (Amended From)

### 5. Critical Files Overview

- **`clarinet_initial_setup.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_initial_setup.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`clarinet_initial_setup.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
