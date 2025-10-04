## Doctype: Clarinet Intake

### 1. Overview and Purpose

**Clarinet Intake** is a submittable doctype in the **Intake** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

**Module:** Intake
**Type:** Submittable Document

This doctype is used to:
- Track business transactions through their lifecycle
- Maintain audit trails with submission and cancellation workflows
- Enforce data integrity through workflow states

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `intake_record_id` | Data | **Unique**, Read-only |
| `intake_date` | Datetime | Read-only. Default: `now` |
| `intake_type` | Select (New Inventory
Repair
Maintenance) | **Required**. Default: `New Inventory` |
| `employee` | Link (User) | Read-only |
| `instrument` | Link (Instrument) | Read-only |
| `intake_status` | Select (Pending
Received
Inspection
Setup
Repair
Awaiting Customer Approval
Awaiting Payment
In Transit
Returned to Customer
Complete
Cancelled) | Read-only. Default: `Pending` |
| `instrument_category` | Link (Instrument Category) | **Required** |
| `manufacturer` | Link (Brand) | **Required** |
| `model` | Data | **Required** |
| `serial_no` | Data | **Required** |
| `clarinet_type` | Select (B♭ Clarinet
A Clarinet
E♭ Clarinet
Bass Clarinet
Alto Clarinet
Contrabass Clarinet
Other) | **Required** |
| `year_of_manufacture` | Int | Year of Manufacture |
| `body_material` | Data | Body Material |
| `key_plating` | Data | Keywork Plating |
| `pitch_standard` | Data | Pitch Standard |
| `bore_type` | Data | Bore Type / Size |
| `tone_hole_style` | Data | Tone Hole Style |
| `thumb_rest_type` | Data | Thumb Rest Type |
| `item_code` | Data | Item Code |
| `item_name` | Data | Item Name |
| ... | ... | *25 more fields* |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_intake.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`after_insert()`**: Executes after a new document is created

**Custom Methods:**
- `on_save()`: Custom business logic method
- `autoname()`: Custom business logic method
- `get_instrument_by_serial()`: Custom business logic method
- `get_instrument_inspection_name()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`clarinet_intake.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes
- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **User** doctype via the `employee` field (Employee / Technician)
- Links to **Instrument** doctype via the `instrument` field (Instrument)
- Links to **Instrument Category** doctype via the `instrument_category` field (Instrument Category)
- Links to **Brand** doctype via the `manufacturer` field (Manufacturer)
- Links to **Customer** doctype via the `customer` field (Customer ID)
- Links to **Work Order** doctype via the `work_order_number` field (Work Order Number)
- Links to **Consent Form** doctype via the `consent_form` field (Consent Form)
- Has child table **Intake Accessory Item** stored in the `accessory_id` field
- Links to **Clarinet Intake** doctype via the `amended_from` field (Amended From)

### 5. Critical Files Overview

- **`clarinet_intake.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_intake.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`clarinet_intake.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_clarinet_intake.py`**: Unit tests for validating doctype functionality
- **`clarinet_intake_list.js`**: Custom list view behavior and interactions

---

*Last updated: 2025-10-04*
