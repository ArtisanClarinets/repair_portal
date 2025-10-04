## Doctype: Repair Quotation

### 1. Overview and Purpose

**Repair Quotation** is a submittable doctype in the **Repair** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

**Module:** Repair
**Type:** Submittable Document

This doctype is used to:
- Track business transactions through their lifecycle
- Maintain audit trails with submission and cancellation workflows
- Enforce data integrity through workflow states

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `title` | Data | **Required**. Default: `Clarinet Repair Quotation` |
| `quotation_date` | Date | **Required** |
| `valid_till` | Date | Valid Till |
| `status` | Select (Draft
Submitted
Cancelled
Expired
Lost
Accepted) | Read-only. Default: `Draft` |
| `contact_email` | Data | Fetched from: `customer_primary_contact.email_id` |
| `contact_phone` | Data | Fetched from: `customer_primary_contact.phone` |
| `company` | Link (Company) | **Required** |
| `currency` | Link (Currency) | **Required**. Fetched from: `customer_name.default_currency` |
| `conversion_rate` | Float | Default: `1` |
| `instrument_type` | Select (B♭ Clarinet
A Clarinet
E♭ Clarinet
C Clarinet
Bass Clarinet) | Instrument Type |
| `brand` | Data | Brand |
| `model` | Data | Model |
| `serial_no` | Data | Serial No. |
| `bore_diameter_mm` | Float | Bore Ø (mm) |
| `condition_notes` | Small Text | Condition Notes |
| `setup_notes` | Small Text | Setup Notes |
| `items` | Table (Repair Quotation Item) | **Required** |
| `terms` | Text Editor | Terms |
| `total_labor` | Currency | Read-only |
| `total_parts` | Currency | Read-only |
| ... | ... | *17 more fields* |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_quotation.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_insert()`**: Runs before a new document is inserted
- **`on_submit()`**: Executes when the document is submitted
- **`on_cancel()`**: Runs when the document is cancelled

**Custom Methods:**
- `make_repair_order()`: Custom business logic method
- `accept_and_make_repair_order()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`repair_quotation.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Company** doctype via the `company` field (Company)
- Links to **Currency** doctype via the `currency` field (Currency)
- Has child table **Repair Quotation Item** stored in the `items` field
- Links to **User** doctype via the `owner_signature` field (Prepared By)
- Links to **User** doctype via the `accepted_by` field (Accepted By)
- Links to **Repair Order** doctype via the `repair_order` field (Repair Order)
- Links to **Customer** doctype via the `customer_name` field (Customer)
- Links to **Contact** doctype via the `customer_primary_contact` field (Contact)
- Links to **Repair Quotation** doctype via the `amended_from` field (Amended From)

### 5. Critical Files Overview

- **`repair_quotation.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_quotation.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`repair_quotation.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
