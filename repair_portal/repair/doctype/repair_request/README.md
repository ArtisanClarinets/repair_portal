## Doctype: Repair Request

### 1. Overview and Purpose

**Repair Request** is a submittable doctype in the **Repair** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

**Module:** Repair
**Type:** Submittable Document

This doctype is used to:
- Track business transactions through their lifecycle
- Maintain audit trails with submission and cancellation workflows
- Enforce data integrity through workflow states

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `customer` | Link (Customer) | **Required** |
| `instrument_category` | Link (Instrument Category) | Instrument Category |
| `date_reported` | Date | Date Reported |
| `promise_date` | Date | Promise Date |
| `issue_description` | Text | **Required** |
| `technician_assigned` | Link (User) | Technician Assigned |
| `priority_level` | Select (
Low
Medium
High) | Default: `Medium` |
| `status` | Select (
Open
In Progress
Resolved
Closed) | Default: `Open` |
| `repair_notes` | Table (Repair Task Log) | Repair Notes |
| `qa_checklist` | Table (Qa Checklist Item) | QA Checklist |
| `amended_from` | Link (Repair Request) | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_request.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`on_submit()`**: Executes when the document is submitted

#### Frontend Logic (JavaScript)

The JavaScript file (`repair_request.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Customer** doctype via the `customer` field (Customer)
- Links to **Instrument Category** doctype via the `instrument_category` field (Instrument Category)
- Links to **User** doctype via the `technician_assigned` field (Technician Assigned)
- Has child table **Repair Task Log** stored in the `repair_notes` field
- Has child table **Qa Checklist Item** stored in the `qa_checklist` field
- Links to **Repair Request** doctype via the `amended_from` field (Amended From)

### 5. Critical Files Overview

- **`repair_request.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_request.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`repair_request.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
