Absolutely — here’s the **updated and refined** version of your `Dashboard Chart` field guide with all valid input types and dependencies included, in a clean, structured markdown format for Frappe v15+:

---

# 📊 Dashboard Chart Field Guide (Frappe v15+)

This guide details all required and optional fields for the `Dashboard Chart` DocType in Frappe/ERPNext, including valid input values and behavior per chart type.

---

## ✅ Standard Required DocType Fields

| Field     | Allowed Values / Format                            |
| --------- | -------------------------------------------------- |
| `doctype` | `"Dashboard Chart"` *(fixed)*                      |
| `name`    | Alphanumeric/underscores; auto-generated or custom |
| `owner`   | Auto-filled username *(system field)*              |
| `label`   | Human-readable title shown in Dashboards           |
| `module`  | Name of module (e.g., `"Selling"`, `"Accounts"`)   |

---

## ✅ Chart-Specific Required Fields

| Field               | Description                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------ |
| `chart_type`        | Type of chart behavior:<br>`Count`, `Sum`, `Average`, `Group By`, `Custom`, `Report`                   |
| `chart_source`      | Name of a defined **Dashboard Chart Source**<br>**Required** for `Custom` or `Report`                  |
| `reference_doctype` | Name of the DocType to query<br>**Required** unless `Custom`/`Report`                                  |
| `based_on_date`     | Field from `reference_doctype` of type `Date`/`Datetime`<br>**Required** for `Count`, `Sum`, `Average` |

---

## 🛠 Optional Fields & Valid Inputs

### 🔹 Aggregation (for `Sum` / `Average`)

| Field            | Description                                       |
| ---------------- | ------------------------------------------------- |
| `based_on_value` | Numeric field (Currency, Float, Int) to aggregate |

---

### 🔹 Grouping (for `Group By`)

| Field               | Valid Values                                               |
| ------------------- | ---------------------------------------------------------- |
| `group_by_based_on` | Any field in `reference_doctype` (e.g., `owner`, `status`) |
| `group_by_type`     | `Count`, `Sum`, `Average`                                  |
| `number_of_groups`  | Integer (e.g., `5`, `10`)                                  |

---

### 🔹 Time/Date Filtering

| Field           | Allowed Values                                                |
| --------------- | ------------------------------------------------------------- |
| `time_interval` | `Hourly`, `Daily`, `Weekly`, `Monthly`, `Quarterly`, `Yearly` |
| `timespan`      | e.g., `Last 7 Days`, `Last Month`, `Last Year`                |
| `from_date`     | Start of range — `"YYYY-MM-DD"`                               |
| `to_date`       | End of range — `"YYYY-MM-DD"`                                 |
| `heatmap_year`  | Four-digit year (e.g., `2025`) — for heatmap charts           |

---

### 🔹 Advanced/Internal Use

| Field                  | Notes                                                       |
| ---------------------- | ----------------------------------------------------------- |
| `filters`              | JSON list of filter conditions (fieldname, operator, value) |
| `report_name`          | Name of Report to use when `chart_type = Report`            |
| `parent_document_type` | Required when `reference_doctype` is a child table          |
| `last_synced_on`       | Auto-filled timestamp (internal)                            |
| `is_custom`            | `1` = User-created variation of standard chart              |
| `is_standard`          | `1` = Shipped with module as fixture                        |
| `disabled`             | `1` = Chart is hidden from UI                               |

---

## 🧭 Quick Field‑to‑Value Mapping

| Field                                  | Valid Values / Type                           |
| -------------------------------------- | --------------------------------------------- |
| `chart_type`                           | Count, Sum, Average, Group By, Custom, Report |
| `chart_source`                         | Dashboard Chart Source name                   |
| `reference_doctype`                    | Any DocType (e.g., Sales Order, Task)         |
| `based_on_date`                        | Date/Datetime field in reference\_doctype     |
| `based_on_value`                       | Currency, Int, or Float field                 |
| `group_by_based_on`                    | Field from reference\_doctype                 |
| `group_by_type`                        | Count, Sum, Average                           |
| `number_of_groups`                     | Integer                                       |
| `time_interval`                        | Hourly, Daily, Weekly, Monthly, etc.          |
| `timespan`                             | Last 30 Days, Last Year, etc.                 |
| `from_date`, `to_date`                 | `"YYYY-MM-DD"` format                         |
| `heatmap_year`                         | 4-digit year                                  |
| `filters`                              | JSON array of filter objects                  |
| `report_name`                          | Report name from Report DocType               |
| `parent_document_type`                 | DocType name                                  |
| `last_synced_on`                       | System-generated timestamp                    |
| `is_custom`, `is_standard`, `disabled` | `0` or `1`                                    |

---

## 🧪 Example Minimal JSON

```json
{
  "doctype": "Dashboard Chart",
  "chart_name": "Open Sales Orders",
  "label": "Open Sales Orders",
  "module": "Selling",
  "chart_type": "Count",
  "reference_doctype": "Sales Order",
  "based_on_date": "transaction_date",
  "time_interval": "Monthly",
  "filters": [
    {
      "fieldname": "status",
      "operator": "=",
      "value": "To Deliver"
    }
  ],
  "is_standard": 0
}
```

---

## ✅ Summary of Core Required Fields

| Field               | Purpose                        |
| ------------------- | ------------------------------ |
| `doctype`           | Always "Dashboard Chart"       |
| `chart_name`        | Internal name                  |
| `label`             | Title shown in UI              |
| `module`            | Owning module                  |
| `chart_type`        | Defines chart logic            |
| `reference_doctype` | Data source DocType            |
| `based_on_date`     | Time-series field for plotting |

---

