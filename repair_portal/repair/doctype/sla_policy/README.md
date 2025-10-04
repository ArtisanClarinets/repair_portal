## Doctype: SLA Policy

### 1. Overview and Purpose

**SLA Policy** is a doctype in the **Repair** module that manages and tracks related business data.

**Module:** Repair
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `policy_name` | Data | **Required**, **Unique** |
| `enabled` | Check | Default: `1` |
| `default_policy` | Check | Default: `0`. If set, this will be used when a Repair Order has no explicit SLA Policy. |
| `apply_per_workshop` | Check | Default: `0`. When enabled, matching rules will consider the Repair Order's Workshop. |
| `breach_grace_minutes` | Int | Default: `0`. Additional minutes allowed after Due time before the SLA is considered breached. |
| `warn_threshold_pct` | Int | Default: `70`. Progress percentage when SLA status turns Yellow. |
| `critical_threshold_pct` | Int | Default: `90`. Progress percentage when SLA status turns Red. |
| `rules` | Table (SLA Policy Rule) | Rules |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`sla_policy.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`on_update()`**: Runs after document updates

#### Frontend Logic (JavaScript)

The JavaScript file (`sla_policy.js`) provides:

- Custom client-side logic and form behaviors

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Has child table **SLA Policy Rule** stored in the `rules` field

### 5. Critical Files Overview

- **`sla_policy.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`sla_policy.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`sla_policy.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_sla_policy.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
