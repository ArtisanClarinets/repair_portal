## Doctype: Instrument Inspection

### 1. Overview and Purpose

**Instrument Inspection** is a submittable doctype in the **Inspection** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

**Module:** Inspection
**Type:** Submittable Document

This doctype is used to:
- Track business transactions through their lifecycle
- Maintain audit trails with submission and cancellation workflows
- Enforce data integrity through workflow states

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `inspection_date` | Date | Default: `Today` |
| `inspection_type` | Select (New Inventory
Repair
Maintenance
QA
Other) | **Required** |
| `serial_no` | Link (Instrument Serial Number) | **Required**, **Unique** |
| `clarinet_intake` | Link (Clarinet Intake) | Clarinet Intake |
| `intake_record_id` | Link (Clarinet Intake) | Intake Record ID |
| `inspected_by` | Link (User) | **Required** |
| `customer` | Link (Customer) | Customer |
| `preliminary_estimate` | Currency | Preliminary Estimate |
| `manufacturer` | Data | Manufacturer |
| `model` | Data | Model |
| `key` | Select (B♭
A
E♭
C
D) | Key |
| `wood_type` | Select (Grenadilla
Mopane
Cocobolo
Synthetic
Other) | Wood Type |
| `unboxing_rh` | Float | Initial Relative Humidity (%) |
| `unboxing_temperature` | Float | Initial Temperature (°C) |
| `unboxing_time` | Datetime | Date and Time of Unboxing |
| `hygrometer_photo` | Attach Image | Hygrometer Reading Photo |
| `rested_unopened` | Check | Default: `0` |
| `acclimatization_controlled_env` | Check | Default: `0` |
| `acclimatization_playing_schedule` | Check | Default: `0` |
| `acclimatization_swabbing` | Check | Default: `0` |
| ... | ... | *30 more fields* |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instrument_inspection.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `before_validate()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`instrument_inspection.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument Serial Number** doctype via the `serial_no` field (Instrument Serial Number)
- Links to **Clarinet Intake** doctype via the `clarinet_intake` field (Clarinet Intake)
- Links to **Clarinet Intake** doctype via the `intake_record_id` field (Intake Record ID)
- Links to **User** doctype via the `inspected_by` field (Inspected By)
- Links to **Customer** doctype via the `customer` field (Customer)
- Has child table **Visual Inspection** stored in the `condition` field
- Has child table **Tenon Measurement** stored in the `tenon_fit_assessment` field
- Has child table **Tone Hole Inspection Record** stored in the `tone_hole_inspection` field
- Has child table **Instrument Photo** stored in the `marketing_photos` field
- Has child table **Instrument Photo** stored in the `service_photos` field
- Has child table **Instrument Accessory** stored in the `accessory_log` field
- Links to **Instrument Inspection** doctype via the `amended_from` field (Amended From)

### 5. Critical Files Overview

- **`instrument_inspection.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instrument_inspection.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`instrument_inspection.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
