## Doctype: Clarinet Setup Task

### 1. Overview and Purpose

**Clarinet Setup Task** is a submittable doctype in the **Instrument Setup** module. It represents a business entity that goes through a lifecycle with draft, submitted, and cancelled states.

**Module:** Instrument Setup
**Type:** Submittable Document

**Description:** Projects-like task used to track clarinet setup/repair work for a single instrument. Supports scheduling, priority, dependencies, progress roll-up to the parent Clarinet Initial Setup, and Gantt/Kanban list modes.

This doctype is used to:
- Track business transactions through their lifecycle
- Maintain audit trails with submission and cancellation workflows
- Enforce data integrity through workflow states

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `clarinet_initial_setup` | Link (Clarinet Initial Setup) | Parent clarinet setup record this task belongs to. Used for filtering, progress roll-up, and navigation. |
| `subject` | Data | **Required**. Short, action-oriented title for the task (e.g., “Set key heights – upper joint”). |
| `status` | Select (Open
Working
Paused
Pending Review
Completed
Canceled) | Default: `Open`. Current state of the task within the setup workflow. |
| `priority` | Select (Low
Medium
High
Urgent) | Default: `Medium`. Priority for scheduling and triage. |
| `progress` | Percent | Default: `0`. Percent complete for this task. Automatically set to 100% when status is Completed; contributes to parent roll-up. |
| `exp_start_date` | Date | Planned start date. Enables Gantt view. |
| `exp_end_date` | Date | Planned end date. Must be on/after Expected Start. Enables Gantt view. |
| `actual_start` | Datetime | Timestamp when work actually started (often set when status moves to Working). |
| `actual_end` | Datetime | Timestamp when work actually completed (often set when status moves to Completed). |
| `depends_on` | Table (Clarinet Task Depends On) | Predecessor tasks that must be Completed before this task can proceed. Each row links to another Clarinet Setup Task. |
| `assigned_to` | Link (User) | User primarily responsible for executing the task. |
| `description` | Text Editor | Detailed procedure, acceptance criteria, measurements, or notes. |
| `instrument` | Link (Instrument) | Instrument record for context (auto-filled from parent where possible). |
| `sequence` | Int | Ordering hint for task lists and generation from templates (use spaced values like 10, 20, 30 to allow inserts). |
| `parent_task` | Link (Clarinet Setup Task) | Optional parent group task (for hierarchical grouping). |
| `is_group` | Check | Default: `0`. If enabled, indicates this is a grouping node (usually not directly actionable). |
| `color` | Color | Optional color tag for visual grouping in list and Kanban views. |
| `serial` | Link (Instrument Serial Number) | Serial number of the instrument being serviced (traceability). |
| `amended_from` | Link (Clarinet Setup Task) | Read-only |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_setup_task.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`on_update()`**: Runs after document updates
- **`on_trash()`**: Executes before document deletion

**Custom Methods:**
- `update_parent_progress_inline()`: Custom business logic method

#### Frontend Logic (JavaScript)

The JavaScript file (`clarinet_setup_task.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Clarinet Initial Setup** doctype via the `clarinet_initial_setup` field (Clarinet Initial Setup)
- Has child table **Clarinet Task Depends On** stored in the `depends_on` field
- Links to **User** doctype via the `assigned_to` field (Assigned To)
- Links to **Instrument** doctype via the `instrument` field (Instrument)
- Links to **Clarinet Setup Task** doctype via the `parent_task` field (Parent Task)
- Links to **Instrument Serial Number** doctype via the `serial` field (Serial No)
- Links to **Clarinet Setup Task** doctype via the `amended_from` field (Amended From)

### 5. Critical Files Overview

- **`clarinet_setup_task.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_setup_task.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`clarinet_setup_task.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`clarinet_setup_task_list.js`**: Custom list view behavior and interactions

---

*Last updated: 2025-10-04*
