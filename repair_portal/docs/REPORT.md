# 📊 REPORT.md

Documentation for Report: **Custom Doctype Report**

---

## 🧾 Metadata

| Field         | Value                |
|---------------|----------------------|
| Report Name   | Custom Doctype Report |
| Doctype       | Custom Doctype |
| Type          | Script Report |
| Module        | Repair Portal      |
| Standard?     | Yes |

---

## 🎛️ Filters

| Fieldname  | Label    | Fieldtype | Options    |
|------------|----------|-----------|------------|
| customer | Customer | Link | Customer |


---

## 📐 Columns

| Label     | Fieldname         | Fieldtype | Width |
|-----------|-------------------|-----------|--------|
| Customer | customer | Data | 120 |
| Issue | issue_description | Data | 200 |


---

## ⚙️ Backend Logic

From `custom_doctype_report.py`:

```python
def execute(filters=None):
    data = frappe.db.get_all("Custom Doctype",
        fields=["customer", "issue_description"],
        filters={{"customer": filters.get("customer")}} if filters else {{}}
    )
    columns = [
        {{"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 120}},
        {{"label": "Issue Description", "fieldname": "issue_description", "fieldtype": "Data", "width": 200}}
    ]
    return columns, data
```


---

## 🔧 Extended Metadata (Available Report Fields)

| Property | Description |
|----------|-------------|
| `report_name` | Unique identifier for the report |
| `ref_doctype` | The Doctype the report is based on |
| `report_type` | Report style: Report Builder, Query Report, Script Report, Custom Report |
| `is_standard` | Yes = included in fixtures; No = custom user report |
| `module` | Owning module name |
| `add_total_row` | Yes/No to append a totals row at bottom |
| `prepared_report` | Yes/No – enables async report generation |
| `disabled` | Yes/No – disables the report in UI |
| `filters` | List of fields to filter the report |
| `columns` | Column headers and structure of the report |
| `roles` | Roles allowed to access the report |
| `ref_doctype_fields` | Optional specific fields used from the Doctype |
