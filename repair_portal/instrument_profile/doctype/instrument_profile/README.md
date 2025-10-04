## Doctype: Instrument Profile

### 1. Overview and Purpose

**Instrument Profile** is a submittable doctype in the **Instrument Profile** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

**Module:** Instrument Profile
**Type:** Submittable Document

This doctype is used to:
- Track business transactions through their lifecycle
- Maintain audit trails with submission and cancellation workflows
- Enforce data integrity through workflow states

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `workflow_state` | Select (Open
In Progress
Delivered
Archived) | Read-only |
| `status` | Data | Read-only. Auto-synced from Instrument.current_status |
| `current_location` | Data | Current Location |
| `instrument_profile_id` | Data | **Unique**, Read-only. Automatically generated unique Instrument Profile ID |
| `instrument` | Link (Instrument) | **Required** |
| `serial_no` | Data | Read-only. Raw serial string from Instrument.serial_no |
| `customer` | Link (Customer) | Read-only |
| `owner_name` | Data | Read-only |
| `headline` | Data | Read-only. Brand Model • Serial |
| `brand` | Data | Read-only. Fetched from: `instrument.brand` |
| `model` | Data | Read-only. Fetched from: `instrument.model` |
| `instrument_category` | Data | Read-only. Auto-synced from Instrument.instrument_type or clarinet_type |
| `wood_type` | Data | Read-only. Fetched from: `instrument.body_material` |
| `body_material` | Data | Body Material |
| `key_plating` | Data | Read-only. Fetched from: `instrument.key_plating` |
| `key_system` | Select (Boehm
Albert
Oehler
Other) | Key System |
| `number_of_keys_rings` | Data | Number of Keys/Rings |
| `purchase_date` | Date | Read-only |
| `purchase_order` | Link (Purchase Order) | Read-only |
| `purchase_receipt` | Link (Purchase Receipt) | Read-only |
| ... | ... | *16 more fields* |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`instrument_profile.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_insert()`**: Runs before a new document is inserted
- **`after_insert()`**: Executes after a new document is created
- **`on_update()`**: Runs after document updates
- **`on_trash()`**: Executes before document deletion

**Custom Methods:**
- `get_instrument_profile_summary()`: Custom business logic method
- `update_instrument_location()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`instrument_profile.js`) provides:

- **Form Refresh**: Updates UI elements when the form loads or refreshes
- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument** doctype via the `instrument` field (Instrument)
- Links to **Customer** doctype via the `customer` field (Customer)
- Links to **Purchase Order** doctype via the `purchase_order` field (Purchase Order)
- Links to **Purchase Receipt** doctype via the `purchase_receipt` field (Purchase Receipt)
- Links to **Instrument Inspection** doctype via the `linked_inspection` field (Instrument Inspection)
- Has child table **Instrument Condition Record** stored in the `condition_logs` field
- Has child table **Customer External Work Log** stored in the `external_work_logs` field
- Has child table **Warranty Modification Log** stored in the `warranty_logs` field
- Has child table **Material Use Log** stored in the `material_usage` field
- Has child table **Instrument Interaction Log** stored in the `interaction_logs` field
- Has child table **Instrument Accessory** stored in the `accessory_log` field
- Has child table **Instrument Photo** stored in the `serial_photos` field
- Has child table **Instrument Photo** stored in the `service_photos` field
- Links to **Instrument Profile** doctype via the `amended_from` field (Amended From)

### 5. Critical Files Overview

- **`instrument_profile.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`instrument_profile.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`instrument_profile.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_instrument_profile.py`**: Unit tests for validating doctype functionality
- **`instrument_profile_list.js`**: Custom list view behavior and interactions

---

*Last updated: 2025-10-04*
