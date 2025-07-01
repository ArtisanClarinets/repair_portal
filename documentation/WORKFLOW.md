# 🔄 WORKFLOW.md

Documentation for Workflow: **Repair Workflow**

---

## 🧾 Metadata

| Field         | Value                |
|---------------|----------------------|
| Workflow Name | Repair Workflow |
| Doctype       | Custom Doctype        |
| Active        | Yes |
| State Field   | status    |

---

## 🔘 States

| State         | DocStatus | Update Field     |
|---------------|-----------|------------------|
| Open | 0 | status |
| In Progress | 0 | - |
| Resolved | 1 | - |
| Closed | 2 | - |


---

## 🔁 Transitions

| From State   | Action     | To State     | Allowed Roles           |
|--------------|------------|--------------|--------------------------|
| Open | Start | In Progress | System Manager |
| In Progress | Resolve | Resolved | System Manager |
| Resolved | Close | Closed | System Manager |


---

## 🔧 Extended Metadata (Workflow Fields)

| Property | Description |
|----------|-------------|
| `workflow_name` | Name of the workflow |
| `doctype` | The DocType this workflow is tied to |
| `is_active` | Whether this workflow is active (1 = Yes) |
| `state_field` | Field that tracks the current workflow state |
| `send_email_alert` | Send notification on state change (Yes/No) |
| `allow_self_approval` | Allow users to approve their own actions |
| `override_status` | Override the default document status updates (Yes/No) |
| `update_field` | Optional — updates a field when entering a state |
| `states` | List of states with associated docstatus and fields |
| `transitions` | List of state changes with permissions |
| `workflow_state_field` | Field used for tracking state (same as state_field) |
