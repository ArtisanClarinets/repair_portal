# WORKSPACE.md — Repair Portal

## Overview
This document provides canonical specifications for defining and registering Workspace documents within the `repair_portal` app. This includes rules, formats, and expected content structure for `Workspace` doctypes, aligned with Frappe v15 standards.

---

## Required Fields

```json
{
  "doctype": "Workspace",
  "name": "Unique Workspace Name",
  "title": "Display Title on UI",
  "label": "Sidebar Label",
  "module": "Valid Module from modules.txt",
  "icon": "fa fa-icon",
  "content": "{\"shortcuts\":[],\"charts\":[],\"links\":[],\"cards\":[]}"
}
```

---

## Field Definitions

| Field     | Description                                  |
|-----------|----------------------------------------------|
| doctype   | Must be "Workspace"                          |
| name      | Internal unique name (same as file name)     |
| title     | Title displayed in page header               |
| label     | Label shown in sidebar navigation            |
| module    | Must match entry in `modules.txt`            |
| icon      | Font Awesome icon for visual identification  |
| content   | Stringified JSON containing UI block data    |

---

## Notes
- The `content` field **must** be a JSON string.
- The module name should exactly match an entry in `repair_portal/modules.txt`.
- The file should be placed at:
  `apps/repair_portal/repair_portal/<module>/workspace/<workspace_name>.json`

---

## Example: Repair Portal Workspace

```json
{
  "doctype": "Workspace",
  "name": "Repair Portal",
  "title": "Repair Portal",
  "label": "Repair Portal",
  "module": "Repair Portal",
  "icon": "fa fa-wrench",
  "content": "{\"shortcuts\":[{\"label\":\"New Repair\",\"type\":\"DocType\",\"name\":\"Custom Doctype\"}],\"charts\":[],\"links\":[],\"cards\":[]}"
}
```

---

## Compliance
This structure is fully compatible with ERPNext v15 / Frappe v15. If updates are made to workspace behavior in core, revisit this guide accordingly.
