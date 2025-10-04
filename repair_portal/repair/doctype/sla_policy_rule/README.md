## Doctype: SLA Policy Rule

### 1. Overview and Purpose

**SLA Policy Rule** is a child table doctype used to store related records within a parent document.

**Module:** Repair
**Type:** Child Table

This doctype is used to:
- Store line items or related records as part of a parent document
- Maintain structured data in a tabular format

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `service_type` | Link (Service Type) | Service Type |
| `workshop` | Link (Workshop) | Workshop |
| `start_event` | Select (Intake Received
Estimate Approved
Work Started) | **Required** |
| `stop_event` | Select (Ready for QA
Delivered) | **Required** |
| `tat_hours` | Int | **Required** |
| `escalation_minutes_1` | Int | Escalation Minutes (Level 1) |
| `escalate_to_role_1` | Link (Role) | Escalate To Role (Level 1) |
| `escalation_minutes_2` | Int | Escalation Minutes (Level 2) |
| `escalate_to_role_2` | Link (Role) | Escalate To Role (Level 2) |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`sla_policy_rule.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

#### Frontend Logic (JavaScript)

The JavaScript file (`sla_policy_rule.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Service Type** doctype via the `service_type` field (Service Type)
- Links to **Workshop** doctype via the `workshop` field (Workshop)
- Links to **Role** doctype via the `escalate_to_role_1` field (Escalate To Role (Level 1))
- Links to **Role** doctype via the `escalate_to_role_2` field (Escalate To Role (Level 2))

### 5. Critical Files Overview

- **`sla_policy_rule.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`sla_policy_rule.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`sla_policy_rule.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_sla_policy_rule.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
