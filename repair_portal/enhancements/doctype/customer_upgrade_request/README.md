## Doctype: Customer Upgrade Request

### 1. Overview and Purpose

**Customer Upgrade Request** is a submittable doctype in the **Enhancements** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

**Module:** Enhancements
**Type:** Submittable Document

This doctype is used to:
- Track business transactions through their lifecycle
- Maintain audit trails with submission and cancellation workflows
- Enforce data integrity through workflow states

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `customer` | Link (Customer) | Customer |
| `requested_upgrades` | Table (Upgrade Option) | Requested Upgrades |
| `notes` | Small Text | Notes |
| `serial` | Link (Instrument) | Instrument |
| `amended_from` | Link (Customer Upgrade Request) | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`customer_upgrade_request.py`) implements the following:

**Lifecycle Hooks:**
- **`on_submit()`**: Executes when the document is submitted

#### Frontend Logic (JavaScript)

The JavaScript file (`customer_upgrade_request.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Customer** doctype via the `customer` field (Customer)
- Has child table **Upgrade Option** stored in the `requested_upgrades` field
- Links to **Instrument** doctype via the `serial` field (Instrument)
- Links to **Customer Upgrade Request** doctype via the `amended_from` field (Amended From)

### 5. Critical Files Overview

- **`customer_upgrade_request.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`customer_upgrade_request.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`customer_upgrade_request.js`**: Client-side script for form behavior, custom buttons, and UI interactions

---

*Last updated: 2025-10-04*
