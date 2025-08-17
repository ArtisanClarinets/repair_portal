# Clarinet Intake (`clarinet_intake`)

## Purpose
The Clarinet Intake DocType records all instrument intake events, whether for new inventory, repair, or maintenance. It acts as the central hub for instrument registration, customer communication, inspection, and workflow initiation.

## Schema Summary
- **Naming:** Auto-assigned via `intake_record_id` (naming series)
- **DocType Type:** Submittable
- **Workflow States:** Pending → Received → Inspection → Setup → Repair → Awaiting Approval → Awaiting Payment → In Transit → Repair Complete → Returned
- **Key Fields:**
  - Instrument Metadata: `instrument_category`, `manufacturer`, `model`, `serial_no`, `clarinet_type`
  - Customer Info: `customer`, `customer_full_name`, `customer_phone`, `customer_email`, `customer_type`
  - Technical Assessments: `wood_body_condition`, `keywork_condition`, `pad_condition`, `spring_condition`, `cork_condition`
  - Service Request: `service_type_requested`, `estimated_cost`, `deposit_paid`, `customer_approval`, `promised_completion_date`
  - Acquisition Data: `acquisition_source`, `acquisition_cost`, `store_asking_price`
  - Attachments: `initial_intake_photos`, `consent_form`
  - Accessories: Child table `Instrument Accessory`

## Business Rules
- Intake type determines required fields:
  - **New Inventory:** Requires `item_code`, `item_name`, `acquisition_cost`, `store_asking_price`
  - **Repair / Maintenance:** Requires `customer`, `customers_stated_issue`
- Each intake auto-generates:
  - **Instrument Serial Number (custom doctype)**
  - **Instrument** record if not already existing
  - **Instrument Inspection** record linked to intake
  - **Clarinet Initial Setup** (for new inventory, if enabled in settings)
- Duplicate serials are prevented by using the ISN utility functions.

## Python Controller Logic
File: `clarinet_intake.py`

- **Class:** `ClarinetIntake(Document)`
- **Hooks:**
  - `after_insert()` → orchestrates item, instrument, ISN, inspection, and setup creation.
  - `autoname()` → generates naming series.
  - `validate()` → enforces dynamic mandatory fields and auto-syncs instrument data.
- **Helpers:**
  - `_compute_inspection_serial_value()` → Handles legacy vs. modern serial link types.
  - `_find_existing_instrument_by_serial()` → Fetches existing instrument by ISN or raw serial.
  - `_sync_info_from_existing_instrument()` → Auto-populates instrument/manufacturer/model fields.
- **Whitelisted Functions:**
  - `get_instrument_by_serial(serial_no)` → returns Instrument metadata.
  - `get_instrument_inspection_name(intake_record_id)` → fetches inspection linked to intake.

## Client-Side Script
File: `clarinet_intake.js`

- **Custom Buttons:**
  - **Settings** → Directs to Clarinet Intake Settings.
  - **Instrument Inspection** → Quick link if inspection exists.
  - **Initial Setup** → Quick link if setup exists for new inventory.
- **Dynamic Required Fields:**  
  Toggles mandatory fields based on `intake_type`.
- **Serial Autofill:**  
  Auto-fills form data when serial is entered, via `get_instrument_by_serial`.

## Integration Points
- **ERPNext Item**: Auto-created for new inventory.
- **Instrument Serial Number**: Centralized tracking.
- **Instrument**: Linked or created per intake.
- **Instrument Inspection**: Automatically linked.
- **Clarinet Initial Setup**: Created for new inventory workflows.
- **Clarinet Intake Settings**: Provides default values, item groups, and automation toggles.

## Validation Standards
- `intake_type`: Must be valid selection (New Inventory, Repair, Maintenance).
- Dynamic field validation per intake type.
- Serial number uniqueness enforced via ISN utilities.
- Customer information mandatory for repairs and maintenance.

## Usage Examples
- **New Inventory:**  
  Intake logs a new Buffet clarinet with auto-created Item, ISN, Instrument, Inspection, and Initial Setup.
- **Repair:**  
  Intake records customer-reported issue, creates inspection, links to existing instrument if serial already known.

## Changelog
- **2025-08-16**: Documentation updated with schema, logic, and integration details.
- **2025-08-14**: Controller updated for robust ISN handling and legacy compatibility.

## Dependencies
- **Frappe Framework**
- **ERPNext Item**
- **Instrument (custom doctype)**
- **Instrument Serial Number (custom doctype)**
- **Instrument Inspection**
- **Clarinet Initial Setup**
- **Clarinet Intake Settings**