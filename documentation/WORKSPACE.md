# 📚 Workspace Management Guide for repair_portal

This guide explains how to create, structure, and register custom Desk Workspaces within the repair_portal Frappe app for Artisan Clarinets.

---

## 1️⃣ Where to Create Workspaces
Create workspace JSON files in each module directory:

```
repair_portal/
├── module_name/
│   └── workspace/
│       └── workspace_name/
│           └── workspace_name.json
```

**Example:**
```
repair_portal/intake/workspace/intake/intake.json
```
Each workspace file defines the UI layout for the Desk (workspace page), including shortcuts, cards, reports, and filters.

---

## 2️⃣ Defining a Workspace JSON (Frappe v15+)

### ✅ Required Top-Level Fields
| Field        | Description                        |
|--------------|------------------------------------|
| doctype      | Always "Workspace"                 |
| name         | Internal, URL-safe identifier      |
| label        | Title shown in sidebar and header  |
| module       | Module name (match folder name)    |
| icon         | FontAwesome, Feather, Octicon      |
| type         | Always "Workspace"                 |
| public       | 1 to make visible to users         |
| parent_page  | (Optional) For nesting             |

---

## 3️⃣ Layout Fields

### 🔹 sections
Sections render blocks of shortcuts in vertical layout.

```json
"sections": [
  {
    "label": "Operations",
    "type": "section",
    "collapsible": 0,
    "items": [
      {
        "type": "shortcut",
        "label": "New Intake",
        "link_to": "Clarinet Intake",
        "link_type": "DocType",
        "icon": "octicon plus",
        "color": "blue"
      }
    ]
  }
]
```

| Field       | Description                           |
|-------------|---------------------------------------|
| label       | Section title                         |
| type        | Always "section"                      |
| collapsible | 1 or 0 to make the section collapsible|
| items       | Array of shortcuts                    |

---

## 4️⃣ Shortcut Item Fields
Each item in a section’s `items` array:

| Field     | Description                            |
|-----------|----------------------------------------|
| type      | Always "shortcut"                      |
| label     | Display text                           |
| link_to   | DocType, Report name, or page path     |
| link_type | "DocType", "Report", "Link", or "Page" |
| icon      | Optional icon                          |
| color     | Optional color (blue, green, etc.)     |

---

## 5️⃣ Cards
Cards group items such as DocTypes and Reports:

```json
"cards": [
  {
    "label": "Documents",
    "items": [
      {
        "type": "doctype",
        "name": "Clarinet Intake"
      }
    ]
  }
]
```

| Field       | Description                       |
|-------------|-----------------------------------|
| type        | "doctype" or "report"             |
| name        | DocType or Report name            |
| report_type | Only for reports (e.g., Script)   |

---

## 6️⃣ Charts (optional)
Used to embed Chart DocTypes:

```json
"charts": [
  {
    "chart_name": "Top Customers",
    "label": "Customer Spend"
  }
]
```

---

## 7️⃣ Onboarding (optional)
Checklist for onboarding:

```json
"onboarding": [
  {
    "label": "Create First Intake",
    "reference_document": "Clarinet Intake"
  }
]
```

---

## 8️⃣ Filters (optional)
Render saved filters:

```json
"filters": [
  {
    "label": "Open Intakes",
    "document_type": "Clarinet Intake",
    "filters_json": "[[\"Clarinet Intake\", \"status\", \"=\", \"Open\"]]"
  }
]
```

---

## 9️⃣ Deprecated Fields
| Field   | Reason                         |
|---------|--------------------------------|
| content| Deprecated in Frappe v15       |

---

## 🔍 Full Sample JSON
```json
{
  "doctype": "Workspace",
  "name": "Intake",
  "label": "Intake",
  "module": "Intake",
  "icon": "inbox",
  "type": "Workspace",
  "public": 1,
  "parent_page": "Repair Portal",
  "sections": [
    {
      "label": "Instrument Intake",
      "type": "section",
      "collapsible": 0,
      "items": [
        {
          "type": "shortcut",
          "label": "New Clarinet Intake",
          "link_to": "Clarinet Intake",
          "link_type": "DocType",
          "color": "blue",
          "icon": "octicon plus"
        }
      ]
    }
  ],
  "cards": [
    {
      "label": "Reports",
      "items": [
        {
          "type": "report",
          "name": "Clarinet Intakes by Status",
          "report_type": "Script Report"
        }
      ]
    }
  ],
  "charts": [],
  "onboarding": 0,
  "filters": []
}
```

---

## 🔗 Registering Modules in desktop.py
To display modules in the Desk UI, update:

```python
# repair_portal/config/desktop.py
from frappe import _

def get_data():
    return [
        {
            "module_name": "Intake",
            "category": "Modules",
            "label": _("Intake"),
            "icon": "fa fa-inbox",
            "type": "module",
            "description": "Instrument Intake and Processing"
        }
    ]
```

---

## 💡 Best Practices
- ✅ Always include at least one section.
- ✅ Use consistent icons and colors.
- ✅ Use `parent_page` to nest under main portal.
- ❌ Do not use `content` field.
- 🔄 After editing: `bench clear-cache && bench restart`

---

## 📦 Deploying Workspaces
Export workspaces as fixtures:
```bash
bench --site yoursite export-fixtures --doctype Workspace
```

---

For questions, contact Dylan Thompson or the Artisan Clarinets workspace maintainer.
