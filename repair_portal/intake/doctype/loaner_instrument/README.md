## Doctype: Loaner Instrument

### 1. Overview and Purpose

**Loaner Instrument** is a submittable doctype in the **Intake** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

**Module:** Intake
**Type:** Submittable Document

This doctype is used to:
- Track business transactions through their lifecycle
- Maintain audit trails with submission and cancellation workflows
- Enforce data integrity through workflow states

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `status` | Select (Draft
Issued
Returned) | **Required**. Default: `Draft` |
| `instrument` | Link (Instrument) | Instrument |
| `intake` | Link (Clarinet Intake) | Intake ID |
| `issued_to` | Link (Customer) | Issued To (Customer) |
| `issued_contact` | Link (Contact) | Issued To (Contact) |
| `issue_date` | Date | **Required** |
| `due_date` | Date | Due Date |
| `returned` | Check | Default: `0` |
| `condition_on_issue` | Small Text | Condition on Issue |
| `condition_on_return` | Small Text | Condition on Return |
| `customer_signature` | Signature | Customer Signature |
| `company_rep_signature` | Signature | Company Representative Signature |
| `agreement_pdf` | Attach | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`loaner_instrument.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `set_loaner_status()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

#### Workflow

This doctype uses a workflow managed by the `status` field to control document states and transitions.

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Instrument** doctype via the `instrument` field (Instrument)
- Links to **Clarinet Intake** doctype via the `intake` field (Intake ID)
- Links to **Customer** doctype via the `issued_to` field (Issued To (Customer))
- Links to **Contact** doctype via the `issued_contact` field (Issued To (Contact))

### 5. Critical Files Overview

- **`loaner_instrument.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`loaner_instrument.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`test_loaner_instrument.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
