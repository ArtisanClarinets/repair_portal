## Doctype: Repair Issue

### 1. Overview and Purpose

**Repair Issue** is a submittable doctype in the **Repair** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

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
| `issue_description` | Text | **Required** |
| `status` | Select (
Open
In Progress
Resolved
Closed) | Default: `Open` |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`repair_issue.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`on_submit()`**: Executes when the document is submitted

**Custom Methods:**
- `autoname()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

#### Workflow

This doctype uses a workflow managed by the `status` field to control document states and transitions.

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Customer** doctype via the `customer` field (Customer)

### 5. Critical Files Overview

- **`repair_issue.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`repair_issue.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
