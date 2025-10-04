## Doctype: Repair Feedback

### 1. Overview and Purpose

**Repair Feedback** is a doctype in the **Repair** module that manages and tracks related business data.

**Module:** Repair
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `repair_order` | Link (Repair Order) | **Required** |
| `customer` | Link (Customer) | **Required** |
| `rating` | Select (1
2
3
4
5) | **Required** |
| `comment` | Small Text | Comment |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_feedback.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Repair Order** doctype via the `repair_order` field (Repair Order)
- Links to **Customer** doctype via the `customer` field (Customer)

### 5. Critical Files Overview

- **`repair_feedback.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_feedback.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
