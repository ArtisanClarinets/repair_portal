# 📘 DOCTYPE.md

Documentation for **Custom Doctype** — part of the Repair Portal module.

---

## 🧾 Meta

| Field           | Value           |
|----------------|------------------|
| Doctype        | Custom Doctype   |
| Module         | Repair Portal    |
| Custom         | No               |
| Editable Grid  | Yes              |
| Is Table       | No               |
| Submittable    | Yes              |
| Workflow Field | status           |

---

## 🧩 Fields

| Fieldname         | Label              | Fieldtype | Required | Options         | Default |
|------------------|--------------------|-----------|----------|-----------------|---------|
| `customer` | Customer | Link | Yes | Customer | - |
| `issue_description` | Issue Description | Text | Yes | - | - |
| `status` | Status | Select | No | 
Open
In Progress
Resolved
Closed | Open |


---

## 🔐 Permissions

| Role            | Read | Write | Create | Delete | Submit | Cancel |
|-----------------|------|-------|--------|--------|--------|--------|
| System Manager | 1 | 1 | 1 | 1 | 1 | 1 |


---

## ⚙️ Controller Methods


```python
def validate(self):
    if not self.customer:
        frappe.throw("Customer is required")

def on_submit(self):
    frappe.msgprint("Document submitted.")
```


---

## 🔧 Extended Metadata (Standard Doctype Fields)

| Property | Description |
|----------|-------------|
| `name` | Custom Doctype |
| `autoname` | Automatically set or custom pattern |
| `document_type` | Main, Single, Child |
| `is_submittable` | Yes |
| `track_changes` | Yes / No |
| `track_views` | Yes / No |
| `track_seen` | Yes / No |
| `email_append_to` | Yes / No |
| `subject` | Fieldname for subject line (if applicable) |
| `sort_field` | Default field to sort by |
| `sort_order` | ASC / DESC |
| `engine` | Storage engine (MariaDB only) |
| `index_web_pages_for_search` | Yes / No |
| `read_only` | Yes / No |
| `in_create` | Show in Create New? Yes / No |
| `search_fields` | Comma-separated list (e.g., customer,status) |
| `title_field` | Field to show as title in header |
| `image_field` | Field to use as image thumbnail |
| `has_web_view` | Yes / No |
| `allow_copy` | Yes / No |
| `show_preview_popup` | Yes / No |
| `workflow_state_field` | Fieldname that stores workflow state |
| `beta` | Yes / No |
| `quick_entry` | Yes / No |
| `is_tree` | Yes / No |
| `allow_auto_repeat` | Yes / No |
| `email_template` | Template for notifications |
| `hide_heading_when_printing` | Yes / No |
