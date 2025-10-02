# Instrument Setup Module — Comprehensive Recursive Documentation

> Auto-generated README covering **every file** and **every function** found in the archive.

## Contents Overview

| File | Type | Lines | Size (bytes) |
|---|---:|---:|---:|
| `.vscode/extensions.json` | json | 14 | 449 |
| `.vscode/settings.json` | json | 3 | 34 |
| `README.md` | markdown | 3 | 162 |
| `__init__.py` | python | 1 | 0 |
| `__pycache__/__init__.cpython-312.pyc` | other | 3 | 184 |
| `config/desktop.py` | python | 20 | 512 |
| `data/clarinet_pad_map_bundled.json` | json | 13 | 297 |
| `data/clarinet_setup_operation_bundled.json` | json | 13 | 288 |
| `data/instrument_model_bundled.json` | json | 15 | 279 |
| `data/setup_checklist_item_bundled.json` | json | 13 | 235 |
| `data/setup_template_bundled.json` | json | 47 | 929 |
| `doctype/__init__.py` | python | 1 | 0 |
| `doctype/__pycache__/__init__.cpython-312.pyc` | other | 3 | 192 |
| `doctype/clarinet_initial_setup/README.md` | markdown | 344 | 14283 |
| `doctype/clarinet_initial_setup/README.md.backup` | other | 213 | 12637 |
| `doctype/clarinet_initial_setup/__init__.py` | python | 1 | 0 |
| `doctype/clarinet_initial_setup/__pycache__/__init__.cpython-312.pyc` | other | 3 | 215 |
| `doctype/clarinet_initial_setup/__pycache__/clarinet_initial_setup.cpython-312.pyc` | other | 113 | 18887 |
| `doctype/clarinet_initial_setup/clarinet_initial_setup.js` | javascript | 248 | 9311 |
| `doctype/clarinet_initial_setup/clarinet_initial_setup.json` | json | 370 | 9196 |
| `doctype/clarinet_initial_setup/clarinet_initial_setup.py` | python | 369 | 16478 |
| `doctype/clarinet_pad_entry/README.md` | markdown | 219 | 8964 |
| `doctype/clarinet_pad_entry/__init__.py` | python | 2 | 26 |
| `doctype/clarinet_pad_entry/__pycache__/__init__.cpython-312.pyc` | other | 3 | 211 |
| `doctype/clarinet_pad_entry/__pycache__/clarinet_pad_entry.cpython-312.pyc` | other | 9 | 1060 |
| `doctype/clarinet_pad_entry/clarinet_pad_entry.json` | json | 71 | 1727 |
| `doctype/clarinet_pad_entry/clarinet_pad_entry.py` | python | 34 | 970 |
| `doctype/clarinet_pad_map/README.md` | markdown | 251 | 10447 |
| `doctype/clarinet_pad_map/__init__.py` | python | 2 | 24 |
| `doctype/clarinet_pad_map/__pycache__/__init__.cpython-312.pyc` | other | 3 | 209 |
| `doctype/clarinet_pad_map/__pycache__/clarinet_pad_map.cpython-312.pyc` | other | 106 | 11844 |
| `doctype/clarinet_pad_map/clarinet_pad_map.js` | javascript | 161 | 5679 |
| `doctype/clarinet_pad_map/clarinet_pad_map.json` | json | 63 | 1350 |
| `doctype/clarinet_pad_map/clarinet_pad_map.py` | python | 405 | 13276 |
| `doctype/clarinet_setup_log/README.md` | markdown | 317 | 12654 |
| `doctype/clarinet_setup_log/__init__.py` | python | 1 | 0 |
| `doctype/clarinet_setup_log/__pycache__/__init__.cpython-312.pyc` | other | 3 | 211 |
| `doctype/clarinet_setup_log/__pycache__/clarinet_setup_log.cpython-312.pyc` | other | 8 | 1131 |
| `doctype/clarinet_setup_log/clarinet_setup_log.js` | javascript | 9 | 186 |
| `doctype/clarinet_setup_log/clarinet_setup_log.json` | json | 108 | 2039 |
| `doctype/clarinet_setup_log/clarinet_setup_log.py` | python | 29 | 853 |
| `doctype/clarinet_setup_operation/README.md` | markdown | 369 | 13990 |
| `doctype/clarinet_setup_operation/__init__.py` | python | 1 | 0 |
| `doctype/clarinet_setup_operation/__pycache__/__init__.cpython-312.pyc` | other | 3 | 217 |
| `doctype/clarinet_setup_operation/__pycache__/clarinet_setup_operation.cpython-312.pyc` | other | 17 | 1316 |
| `doctype/clarinet_setup_operation/clarinet_setup_operation.json` | json | 64 | 1516 |
| `doctype/clarinet_setup_operation/clarinet_setup_operation.py` | python | 39 | 1209 |
| `doctype/clarinet_setup_task/README.md` | markdown | 330 | 12703 |
| `doctype/clarinet_setup_task/__init__.py` | python | 1 | 0 |
| `doctype/clarinet_setup_task/__pycache__/__init__.cpython-312.pyc` | other | 3 | 212 |
| `doctype/clarinet_setup_task/__pycache__/clarinet_setup_task.cpython-312.pyc` | other | 39 | 4969 |
| `doctype/clarinet_setup_task/clarinet_setup_task.js` | javascript | 118 | 3900 |
| `doctype/clarinet_setup_task/clarinet_setup_task.json` | json | 213 | 5669 |
| `doctype/clarinet_setup_task/clarinet_setup_task.py` | python | 106 | 4092 |
| `doctype/clarinet_setup_task/clarinet_setup_task_list.js` | javascript | 38 | 1993 |
| `doctype/clarinet_task_depends_on/README.md` | markdown | 324 | 11934 |
| `doctype/clarinet_task_depends_on/__init__.py` | python | 1 | 0 |
| `doctype/clarinet_task_depends_on/__pycache__/__init__.cpython-312.pyc` | other | 3 | 217 |
| `doctype/clarinet_task_depends_on/__pycache__/clarinet_task_depends_on.cpython-312.pyc` | other | 8 | 809 |
| `doctype/clarinet_task_depends_on/clarinet_task_depends_on.js` | javascript | 13 | 463 |
| `doctype/clarinet_task_depends_on/clarinet_task_depends_on.json` | json | 36 | 974 |
| `doctype/clarinet_task_depends_on/clarinet_task_depends_on.py` | python | 27 | 757 |
| `doctype/clarinet_template_task/README.md` | markdown | 271 | 9865 |
| `doctype/clarinet_template_task/__init__.py` | python | 1 | 0 |
| `doctype/clarinet_template_task/__pycache__/__init__.cpython-312.pyc` | other | 3 | 215 |
| `doctype/clarinet_template_task/__pycache__/clarinet_template_task.cpython-312.pyc` | other | 19 | 1397 |
| `doctype/clarinet_template_task/clarinet_template_task.js` | javascript | 9 | 178 |
| `doctype/clarinet_template_task/clarinet_template_task.json` | json | 85 | 2404 |
| `doctype/clarinet_template_task/clarinet_template_task.py` | python | 34 | 1195 |
| `doctype/clarinet_template_task_depends_on/README.md` | markdown | 165 | 6304 |
| `doctype/clarinet_template_task_depends_on/__init__.py` | python | 6 | 278 |
| `doctype/clarinet_template_task_depends_on/__pycache__/__init__.cpython-312.pyc` | other | 3 | 226 |
| `doctype/clarinet_template_task_depends_on/__pycache__/clarinet_template_task_depends_on.cpython-312.pyc` | other | 8 | 844 |
| `doctype/clarinet_template_task_depends_on/clarinet_template_task_depends_on.json` | json | 44 | 1233 |
| `doctype/clarinet_template_task_depends_on/clarinet_template_task_depends_on.py` | python | 26 | 869 |
| `doctype/setup_checklist_item/README.md` | markdown | 347 | 13435 |
| `doctype/setup_checklist_item/__init__.py` | python | 1 | 0 |
| `doctype/setup_checklist_item/__pycache__/__init__.cpython-312.pyc` | other | 3 | 213 |
| `doctype/setup_checklist_item/__pycache__/setup_checklist_item.cpython-312.pyc` | other | 7 | 924 |
| `doctype/setup_checklist_item/setup_checklist_item.json` | json | 45 | 854 |
| `doctype/setup_checklist_item/setup_checklist_item.py` | python | 26 | 726 |
| `doctype/setup_material_log/README.md` | markdown | 228 | 8499 |
| `doctype/setup_material_log/__init__.py` | python | 1 | 0 |
| `doctype/setup_material_log/__pycache__/__init__.cpython-312.pyc` | other | 3 | 211 |
| `doctype/setup_material_log/__pycache__/setup_material_log.cpython-312.pyc` | other | 14 | 1243 |
| `doctype/setup_material_log/setup_material_log.js` | javascript | 39 | 1184 |
| `doctype/setup_material_log/setup_material_log.json` | json | 75 | 1871 |
| `doctype/setup_material_log/setup_material_log.py` | python | 35 | 930 |
| `doctype/setup_template/README.md` | markdown | 304 | 14259 |
| `doctype/setup_template/__init__.py` | python | 1 | 0 |
| `doctype/setup_template/__pycache__/__init__.cpython-312.pyc` | other | 3 | 207 |
| `doctype/setup_template/__pycache__/setup_template.cpython-312.pyc` | other | 70 | 9243 |
| `doctype/setup_template/setup_template.js` | javascript | 204 | 7131 |
| `doctype/setup_template/setup_template.json` | json | 186 | 5501 |
| `doctype/setup_template/setup_template.py` | python | 195 | 8219 |
| `hooks/after_install/create_a_clarinet_standard_template.py` | python | 223 | 14265 |
| `hooks/after_install/create_bb_clarinet_standard_template.py` | python | 223 | 13061 |
| `hooks/after_install/create_eb_clarinet_standard_template.py` | python | 223 | 14335 |
| `hooks/load_templates.py` | python | 78 | 2934 |
| `hooks/templates/brand_bundled.json` | json | 23 | 508 |
| `hooks/templates/create_a_clarinet_standard_template.json` | json | 43 | 8268 |
| `hooks/templates/create_bb_clarinet_standard_template.json` | json | 166 | 7836 |
| `hooks/templates/instrument_model_import.json` | json | 82 | 2288 |
| `print_format/__init__.py` | python | 1 | 0 |
| `print_format/clarinet_setup_certificate/README.md` | markdown | 21 | 743 |
| `print_format/clarinet_setup_certificate/__init__.py` | python | 1 | 0 |
| `print_format/clarinet_setup_certificate/clarinet_setup_certificate.html` | html | 357 | 14170 |
| `print_format/clarinet_setup_certificate/clarinet_setup_certificate.json` | json | 33 | 1538 |
| `report/parts_consumption/parts_consumption.json` | json | 11 | 311 |
| `report/parts_consumption/parts_consumption.py` | python | 23 | 546 |
| `report/technician_performance/technician_performance.json` | json | 11 | 321 |
| `report/technician_performance/technician_performance.py` | python | 32 | 880 |
| `report/turnaround_time_analysis/turnaround_time_analysis.json` | json | 28 | 534 |
| `report/turnaround_time_analysis/turnaround_time_analysis.sql` | other | 12 | 302 |
| `web_form/repair_status/repair_status.json` | json | 32 | 588 |

---

## `.vscode/extensions.json`
- **Type:** json  
- **Lines:** 14  
- **Size:** 449 bytes  

(JSON parsed but not a dict top-level.)

---

## `.vscode/settings.json`
- **Type:** json  
- **Lines:** 3  
- **Size:** 34 bytes  

---

## `README.md`
- **Type:** markdown  
- **Lines:** 3  
- **Size:** 162 bytes  

(Markdown file; content summarized.)

---

## `__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 184 bytes  

---

## `config/desktop.py`
- **Type:** python  
- **Lines:** 20  
- **Size:** 512 bytes  

### Functions
- **L9 — `get_data()`**
  - Doc: No docstring provided.

---

## `data/clarinet_pad_map_bundled.json`
- **Type:** json  
- **Lines:** 13  
- **Size:** 297 bytes  

(JSON parsed but not a dict top-level.)

---

## `data/clarinet_setup_operation_bundled.json`
- **Type:** json  
- **Lines:** 13  
- **Size:** 288 bytes  

(JSON parsed but not a dict top-level.)

---

## `data/instrument_model_bundled.json`
- **Type:** json  
- **Lines:** 15  
- **Size:** 279 bytes  

(JSON parsed but not a dict top-level.)

---

## `data/setup_checklist_item_bundled.json`
- **Type:** json  
- **Lines:** 13  
- **Size:** 235 bytes  

(JSON parsed but not a dict top-level.)

---

## `data/setup_template_bundled.json`
- **Type:** json  
- **Lines:** 47  
- **Size:** 929 bytes  

(JSON parsed but not a dict top-level.)

---

## `doctype/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `doctype/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 192 bytes  

---

## `doctype/clarinet_initial_setup/README.md`
- **Type:** markdown  
- **Lines:** 344  
- **Size:** 14283 bytes  

(Markdown file; content summarized.)

---

## `doctype/clarinet_initial_setup/README.md.backup`
- **Type:** other  
- **Lines:** 213  
- **Size:** 12637 bytes  

---

## `doctype/clarinet_initial_setup/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `doctype/clarinet_initial_setup/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 215 bytes  

---

## `doctype/clarinet_initial_setup/__pycache__/clarinet_initial_setup.cpython-312.pyc`
- **Type:** other  
- **Lines:** 113  
- **Size:** 18887 bytes  

---

## `doctype/clarinet_initial_setup/clarinet_initial_setup.js`
- **Type:** javascript  
- **Lines:** 248  
- **Size:** 9311 bytes  

### Scripted behaviors / functions
- `apply_setup_template(frm)`
- `set_headline(frm)`
- `show_progress(frm)`
- `show_project_timeline(frm)`
- `calculate_expected_end_date(frm)`
- `calculate_estimated_costs(frm)`
- `update_status_indicators(frm)`
- `add_draft_buttons(frm)`
- `add_nav_buttons(frm)`
- `add_certificate_button(frm)`
- `ensure_saved(frm)`
- `frappe.ui.form.on(Clarinet Initial Setup)(frm)`

---

## `doctype/clarinet_initial_setup/clarinet_initial_setup.json`
- **Type:** json  
- **Lines:** 370  
- **Size:** 9196 bytes  

### DocType Definition
- **Name:** Clarinet Initial Setup
- **Module:** Instrument Setup
- **Autoname:** format: CSU-{YY}{MM}-{####}
- **Fields:** 42

#### Fields
- `project_info_section` — Section Break — reqd=0 — label=Project Information
- `status` — Select — reqd=0 — label=Status
- `priority` — Select — reqd=0 — label=Priority
- `setup_type` — Select — reqd=0 — label=Setup Type
- `column_break_project` — Column Break — reqd=0 — label=
- `expected_start_date` — Date — reqd=0 — label=Expected Start Date
- `expected_end_date` — Date — reqd=0 — label=Expected End Date
- `actual_start_date` — Datetime — reqd=0 — label=Actual Start Date
- `actual_end_date` — Datetime — reqd=0 — label=Actual End Date
- `progress` — Percent — reqd=0 — label=Progress
- `instrument_information_section` — Section Break — reqd=0 — label=Instrument Information
- `serial` — Link — reqd=0 — label=Serial No
- `instrument` — Link — reqd=1 — label=Instrument
- `instrument_profile` — Link — reqd=0 — label=Instrument Profile
- `clarinet_type` — Select — reqd=0 — label=Type of Clarinet
- `model` — Data — reqd=0 — label=Model
- `column_break_instrument` — Column Break — reqd=0 — label=
- `intake` — Link — reqd=0 — label=Intake
- `inspection` — Link — reqd=0 — label=Inspection
- `project_details_section` — Section Break — reqd=0 — label=Project Details
- `technician` — Link — reqd=0 — label=Technician
- `setup_date` — Date — reqd=0 — label=Setup Date
- `labor_hours` — Float — reqd=0 — label=Labor Hours
- `column_break_details` — Column Break — reqd=0 — label=
- `estimated_cost` — Currency — reqd=0 — label=Estimated Cost
- `actual_cost` — Currency — reqd=0 — label=Actual Cost
- `estimated_materials_cost` — Currency — reqd=0 — label=Estimated Materials Cost
- `actual_materials_cost` — Currency — reqd=0 — label=Actual Materials Cost
- `setup_content_section` — Section Break — reqd=0 — label=Setup Content
- `setup_template` — Link — reqd=0 — label=Setup Template
- `checklist` — Table — reqd=0 — label=Checklist
- `operations_performed` — Table — reqd=0 — label=Operations Performed
- `col_setup_right` — Column Break — reqd=0 — label=
- `materials_used` — Table — reqd=0 — label=Materials Used
- `setup_logs_section` — Section Break — reqd=0 — label=Setup Logs & Notes
- `notes` — Table — reqd=0 — label=Setup Logs
- `technical_tags` — Text Editor — reqd=0 — label=Technical Tags/Notes
- `sec_media` — Section Break — reqd=0 — label=Media
- `work_photos` — Attach Image — reqd=0 — label=Work Photos
- `sec_audit` — Section Break — reqd=0 — label=Audit & Reference
- `clarinet_initial_setup_id` — Data — reqd=0 — label=Setup ID
- `amended_from` — Link — reqd=0 — label=Amended From

---

## `doctype/clarinet_initial_setup/clarinet_initial_setup.py`
- **Type:** python  
- **Lines:** 369  
- **Size:** 16478 bytes  

### Functions
- **L23 — `_get_setting(field, default) -> float`**
  - Doc: Safely fetch a numeric single-value setting. Accepts int/float and numeric strings.
Returns the default for None, empty string, non-numeric strings, or unsupported types
such as date/datetime to avoid passing them to float().
- **L104 — `before_insert(self)`**
  - Doc: No docstring provided.
- **L110 — `validate(self)`**
  - Doc: No docstring provided.
- **L117 — `on_update_after_submit(self)`**
  - Doc: Update actual dates based on status changes.
- **L121 — `on_submit(self)`**
  - Doc: No docstring provided.
- **L136 — `set_defaults_from_template(self)`**
  - Doc: Set default values from selected template (server-side).
- **L160 — `set_project_dates(self)`**
  - Doc: Set project timeline dates. Uses hours_per_day setting.
- **L173 — `validate_project_dates(self)`**
  - Doc: Validate project timeline consistency.
- **L183 — `update_actual_dates(self)`**
  - Doc: Update actual dates based on status.
- **L190 — `calculate_costs(self)`**
  - Doc: Calculate actual costs from materials used + labor hours.
- **L206 — `ensure_checklist(self)`**
  - Doc: No docstring provided.
- **L211 — `load_operations_from_template(self)`**
  - Decorators: `frappe.whitelist()`
  - Doc: Load default operations and checklist from the selected setup template.
- **L261 — `create_tasks_from_template(self) -> dict`**
  - Decorators: `frappe.whitelist()`
  - Doc: Create Clarinet Setup Task docs from the linked Setup Template.
- Uses exp_duration_mins primarily; falls back to exp_duration_days for legacy rows.
- Maps minutes to calendar dates:
    span_days = max(1, ceil(minutes / 1440))
    exp_end_date = exp_start_date + (span_days - 1)
- **L321 — `generate_certificate(self, print_format, attach, return_file_url)`**
  - Decorators: `frappe.whitelist()`
  - Doc: Render the Print Format and (optionally) attach the PDF; return a URL when requested.
- **L359 — `update_parent_progress(initial_setup)`**
  - Decorators: `frappe.whitelist()`
  - Doc: No docstring provided.

### Classes
- **L58 — `class ClarinetInitialSetup(Document)`**
  - Doc: No class docstring provided.
  - **Methods:**
    - L104 — `before_insert(self)` — No method docstring provided.
    - L110 — `validate(self)` — No method docstring provided.
    - L117 — `on_update_after_submit(self)` — Update actual dates based on status changes.
    - L121 — `on_submit(self)` — No method docstring provided.
    - L136 — `set_defaults_from_template(self)` — Set default values from selected template (server-side).
    - L160 — `set_project_dates(self)` — Set project timeline dates. Uses hours_per_day setting.
    - L173 — `validate_project_dates(self)` — Validate project timeline consistency.
    - L183 — `update_actual_dates(self)` — Update actual dates based on status.
    - L190 — `calculate_costs(self)` — Calculate actual costs from materials used + labor hours.
    - L206 — `ensure_checklist(self)` — No method docstring provided.
    - L211 — `load_operations_from_template(self)` — Load default operations and checklist from the selected setup template.
    - L261 — `create_tasks_from_template(self)` — Create Clarinet Setup Task docs from the linked Setup Template.
- Uses exp_duration_mins primarily; falls back to exp_duration_days for legacy rows.
- Maps minutes to calendar dates:
    span_days = max(1, ceil(minutes / 1440))
    exp_end_date = exp_start_date + (span_days - 1)
    - L321 — `generate_certificate(self, print_format, attach, return_file_url)` — Render the Print Format and (optionally) attach the PDF; return a URL when requested.

---

## `doctype/clarinet_pad_entry/README.md`
- **Type:** markdown  
- **Lines:** 219  
- **Size:** 8964 bytes  

(Markdown file; content summarized.)

---

## `doctype/clarinet_pad_entry/__init__.py`
- **Type:** python  
- **Lines:** 2  
- **Size:** 26 bytes  

---

## `doctype/clarinet_pad_entry/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 211 bytes  

---

## `doctype/clarinet_pad_entry/__pycache__/clarinet_pad_entry.cpython-312.pyc`
- **Type:** other  
- **Lines:** 9  
- **Size:** 1060 bytes  

---

## `doctype/clarinet_pad_entry/clarinet_pad_entry.json`
- **Type:** json  
- **Lines:** 71  
- **Size:** 1727 bytes  

### DocType Definition
- **Name:** Clarinet Pad Entry
- **Module:** Instrument Setup
- **Autoname:** format:CPE-{#####}
- **Fields:** 6

#### Fields
- `pad_position` — Data — reqd=0 — label=Pad Position
- `is_secondary_pad` — Check — reqd=0 — label=Is Secondary Pad
- `parent_pad` — Link — reqd=0 — label=Parent Pad
- `pad_type` — Data — reqd=0 — label=Pad Type
- `is_open_key` — Check — reqd=0 — label=Is Open Key
- `section_break_vhmi` — Section Break — reqd=0 — label=

---

## `doctype/clarinet_pad_entry/clarinet_pad_entry.py`
- **Type:** python  
- **Lines:** 34  
- **Size:** 970 bytes  

### Classes
- **L11 — `class ClarinetPadEntry(Document)`**
  - Doc: No class docstring provided.

---

## `doctype/clarinet_pad_map/README.md`
- **Type:** markdown  
- **Lines:** 251  
- **Size:** 10447 bytes  

(Markdown file; content summarized.)

---

## `doctype/clarinet_pad_map/__init__.py`
- **Type:** python  
- **Lines:** 2  
- **Size:** 24 bytes  

---

## `doctype/clarinet_pad_map/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 209 bytes  

---

## `doctype/clarinet_pad_map/__pycache__/clarinet_pad_map.cpython-312.pyc`
- **Type:** other  
- **Lines:** 106  
- **Size:** 11844 bytes  

---

## `doctype/clarinet_pad_map/clarinet_pad_map.js`
- **Type:** javascript  
- **Lines:** 161  
- **Size:** 5679 bytes  

### Scripted behaviors / functions
- `looks_like_bass(category_title)`
- `should_autopopulate(frm)`
- `call_server_populate(frm)`
- `frappe.ui.form.on(Clarinet Pad Map)(frm)`
- `frappe.ui.form.on(Clarinet Pad Entry)(frm)`

---

## `doctype/clarinet_pad_map/clarinet_pad_map.json`
- **Type:** json  
- **Lines:** 63  
- **Size:** 1350 bytes  

### DocType Definition
- **Name:** Clarinet Pad Map
- **Module:** Instrument Setup
- **Autoname:** format:PAD-MAP-{clarinet_model}
- **Fields:** 4

#### Fields
- `clarinet_model` — Link — reqd=0 — label=Clarinet Model
- `top_joint_pads` — Table — reqd=0 — label=Top Joint Pads
- `bottom_joint_pads` — Table — reqd=0 — label=Bottom Joint Pads
- `instrument_category` — Link — reqd=0 — label=Instrument Key 

---

## `doctype/clarinet_pad_map/clarinet_pad_map.py`
- **Type:** python  
- **Lines:** 405  
- **Size:** 13276 bytes  

### Functions
- **L57 — `_normalize_title(s) -> str`**
  - Doc: No docstring provided.
- **L189 — `validate(self)`**
  - Doc: No docstring provided.
- **L203 — `_get_category_title_from_links(self) -> str | None`**
  - Doc: Resolve the category title using either:
  - instrument_category (Link to Instrument Category), or
  - clarinet_model/instrument_model -> Instrument Category -> title
Returns title (string) or None.
- **L235 — `get_clarinet_type(self) -> str | None`**
  - Doc: Backward-compatible helper (kept for any external callers).
- **L239 — `_detect_family_variant(self) -> tuple[str | None, str | None]`**
  - Doc: Determine whether the linked Instrument Category corresponds to a soprano or bass,
and for bass, which low-note variant (low_eb, low_c, low_d_extension).

Returns: (family, variant)
  family ∈ {"soprano","bass",None}
  variant ∈ {"low_eb","low_c","low_d_extension",None}
- **L275 — `_populate_soprano(self)`**
  - Doc: No docstring provided.
- **L293 — `_populate_bass(self, variant)`**
  - Doc: No docstring provided.
- **L317 — `_enforce_open_key_flags(self, family)`**
  - Doc: Set a default is_open_key only when the field is unset.
- If pad_position is in OPEN set and is_open_key is unset -> set to 1
- If pad_position is not in OPEN set and is_open_key is unset -> set to 0
- If user already set 0 or 1 -> DO NOT change it
- **L332 — `_normalize(v)`**
  - Doc: No docstring provided.
- **L339 — `_apply(rows)`**
  - Doc: No docstring provided.
- **L358 — `populate_standard_pad_names(docname, doc_json)`**
  - Decorators: `frappe.whitelist(allow_guest=False)`
  - Doc: Populate pads for a Clarinet Pad Map.

Use either:
  - docname: saved Document name → populate + save, returns True
  - doc_json: full Document dict (unsaved) → populate in-memory, returns rows (no save)
- **L367 — `_populate_and_enforce(_doc)`**
  - Doc: No docstring provided.

### Classes
- **L162 — `class ClarinetPadMap(Document)`**
  - Doc: No class docstring provided.
  - **Methods:**
    - L189 — `validate(self)` — No method docstring provided.
    - L203 — `_get_category_title_from_links(self)` — Resolve the category title using either:
  - instrument_category (Link to Instrument Category), or
  - clarinet_model/instrument_model -> Instrument Category -> title
Returns title (string) or None.
    - L235 — `get_clarinet_type(self)` — Backward-compatible helper (kept for any external callers).
    - L239 — `_detect_family_variant(self)` — Determine whether the linked Instrument Category corresponds to a soprano or bass,
and for bass, which low-note variant (low_eb, low_c, low_d_extension).

Returns: (family, variant)
  family ∈ {"soprano","bass",None}
  variant ∈ {"low_eb","low_c","low_d_extension",None}
    - L275 — `_populate_soprano(self)` — No method docstring provided.
    - L293 — `_populate_bass(self, variant)` — No method docstring provided.
    - L317 — `_enforce_open_key_flags(self, family)` — Set a default is_open_key only when the field is unset.
- If pad_position is in OPEN set and is_open_key is unset -> set to 1
- If pad_position is not in OPEN set and is_open_key is unset -> set to 0
- If user already set 0 or 1 -> DO NOT change it

---

## `doctype/clarinet_setup_log/README.md`
- **Type:** markdown  
- **Lines:** 317  
- **Size:** 12654 bytes  

(Markdown file; content summarized.)

---

## `doctype/clarinet_setup_log/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `doctype/clarinet_setup_log/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 211 bytes  

---

## `doctype/clarinet_setup_log/__pycache__/clarinet_setup_log.cpython-312.pyc`
- **Type:** other  
- **Lines:** 8  
- **Size:** 1131 bytes  

---

## `doctype/clarinet_setup_log/clarinet_setup_log.js`
- **Type:** javascript  
- **Lines:** 9  
- **Size:** 186 bytes  

### Scripted behaviors / functions
- `frappe.ui.form.on(Clarinet Setup Log)(frm)`

---

## `doctype/clarinet_setup_log/clarinet_setup_log.json`
- **Type:** json  
- **Lines:** 108  
- **Size:** 2039 bytes  

### DocType Definition
- **Name:** Clarinet Setup Log
- **Module:** Instrument Setup
- **Autoname:** format:CSL-{YY}{MM}-{#####}
- **Fields:** 9

#### Fields
- `customer` — Link — reqd=1 — label=Customer
- `initial_setup` — Link — reqd=1 — label=Initial Setup
- `log_time` — Datetime — reqd=0 — label=Log Time
- `instrument_profile` — Link — reqd=1 — label=Instrument Profile
- `description` — Text — reqd=0 — label=Description
- `action_by` — Link — reqd=0 — label=Action By
- `notes` — Text — reqd=0 — label=Notes
- `attachments` — Attach — reqd=0 — label=Attachments
- `serial` — Link — reqd=1 — label=Serial Number

---

## `doctype/clarinet_setup_log/clarinet_setup_log.py`
- **Type:** python  
- **Lines:** 29  
- **Size:** 853 bytes  

### Classes
- **L9 — `class ClarinetSetupLog(Document)`**
  - Doc: No class docstring provided.

---

## `doctype/clarinet_setup_operation/README.md`
- **Type:** markdown  
- **Lines:** 369  
- **Size:** 13990 bytes  

(Markdown file; content summarized.)

---

## `doctype/clarinet_setup_operation/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `doctype/clarinet_setup_operation/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 217 bytes  

---

## `doctype/clarinet_setup_operation/__pycache__/clarinet_setup_operation.cpython-312.pyc`
- **Type:** other  
- **Lines:** 17  
- **Size:** 1316 bytes  

---

## `doctype/clarinet_setup_operation/clarinet_setup_operation.json`
- **Type:** json  
- **Lines:** 64  
- **Size:** 1516 bytes  

### DocType Definition
- **Name:** Clarinet Setup Operation
- **Module:** Instrument Setup
- **Autoname:** format:CSO-{#####}
- **Fields:** 5

#### Fields
- `operation_type` — Select — reqd=0 — label=Operation Type
- `section` — Select — reqd=0 — label=Section
- `component_ref` — Data — reqd=0 — label=Component Ref (Tone Hole, Key, etc.)
- `details` — Text — reqd=0 — label=Details / Notes
- `completed` — Check — reqd=0 — label=Completed

---

## `doctype/clarinet_setup_operation/clarinet_setup_operation.py`
- **Type:** python  
- **Lines:** 39  
- **Size:** 1209 bytes  

### Classes
- **L9 — `class ClarinetSetupOperation(Document)`**
  - Doc: No class docstring provided.

---

## `doctype/clarinet_setup_task/README.md`
- **Type:** markdown  
- **Lines:** 330  
- **Size:** 12703 bytes  

(Markdown file; content summarized.)

---

## `doctype/clarinet_setup_task/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `doctype/clarinet_setup_task/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 212 bytes  

---

## `doctype/clarinet_setup_task/__pycache__/clarinet_setup_task.cpython-312.pyc`
- **Type:** other  
- **Lines:** 39  
- **Size:** 4969 bytes  

---

## `doctype/clarinet_setup_task/clarinet_setup_task.js`
- **Type:** javascript  
- **Lines:** 118  
- **Size:** 3900 bytes  

### Scripted behaviors / functions
- `show_status_banner(frm)`
- `add_status_buttons(frm)`
- `set_status(frm, new_status, extra = {})`
- `show_dependency_summary(frm)`
- `frappe.ui.form.on(Clarinet Setup Task)(frm)`

---

## `doctype/clarinet_setup_task/clarinet_setup_task.json`
- **Type:** json  
- **Lines:** 213  
- **Size:** 5669 bytes  

### DocType Definition
- **Name:** Clarinet Setup Task
- **Module:** Instrument Setup
- **Autoname:** format:CST-{#####}
- **Fields:** 19

#### Fields
- `clarinet_initial_setup` — Link — reqd=0 — label=Clarinet Initial Setup
- `subject` — Data — reqd=1 — label=Subject
- `status` — Select — reqd=0 — label=Status
- `priority` — Select — reqd=0 — label=Priority
- `progress` — Percent — reqd=0 — label=Progress
- `exp_start_date` — Date — reqd=0 — label=Expected Start
- `exp_end_date` — Date — reqd=0 — label=Expected End
- `actual_start` — Datetime — reqd=0 — label=Actual Start
- `actual_end` — Datetime — reqd=0 — label=Actual End
- `depends_on` — Table — reqd=0 — label=Depends On
- `assigned_to` — Link — reqd=0 — label=Assigned To
- `description` — Text Editor — reqd=0 — label=Description
- `instrument` — Link — reqd=0 — label=Instrument
- `sequence` — Int — reqd=0 — label=Sequence
- `parent_task` — Link — reqd=0 — label=Parent Task
- `is_group` — Check — reqd=0 — label=Is Group
- `color` — Color — reqd=0 — label=Color
- `serial` — Link — reqd=0 — label=Serial No
- `amended_from` — Link — reqd=0 — label=Amended From

---

## `doctype/clarinet_setup_task/clarinet_setup_task.py`
- **Type:** python  
- **Lines:** 106  
- **Size:** 4092 bytes  

### Functions
- **L48 — `validate(self)`**
  - Doc: No docstring provided.
- **L76 — `on_update(self)`**
  - Doc: No docstring provided.
- **L89 — `on_trash(self)`**
  - Doc: No docstring provided.
- **L94 — `update_parent_progress_inline(initial_setup)`**
  - Doc: Inline (non-queued) parent progress roll-up fallback.

### Classes
- **L14 — `class ClarinetSetupTask(Document)`**
  - Doc: No class docstring provided.
  - **Methods:**
    - L48 — `validate(self)` — No method docstring provided.
    - L76 — `on_update(self)` — No method docstring provided.
    - L89 — `on_trash(self)` — No method docstring provided.

---

## `doctype/clarinet_setup_task/clarinet_setup_task_list.js`
- **Type:** javascript  
- **Lines:** 38  
- **Size:** 1993 bytes  

_No explicit functions found via static regex scan._

---

## `doctype/clarinet_task_depends_on/README.md`
- **Type:** markdown  
- **Lines:** 324  
- **Size:** 11934 bytes  

(Markdown file; content summarized.)

---

## `doctype/clarinet_task_depends_on/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `doctype/clarinet_task_depends_on/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 217 bytes  

---

## `doctype/clarinet_task_depends_on/__pycache__/clarinet_task_depends_on.cpython-312.pyc`
- **Type:** other  
- **Lines:** 8  
- **Size:** 809 bytes  

---

## `doctype/clarinet_task_depends_on/clarinet_task_depends_on.js`
- **Type:** javascript  
- **Lines:** 13  
- **Size:** 463 bytes  

### Scripted behaviors / functions
- `frappe.ui.form.on(Clarinet Task Depends On)(frm)`

---

## `doctype/clarinet_task_depends_on/clarinet_task_depends_on.json`
- **Type:** json  
- **Lines:** 36  
- **Size:** 974 bytes  

### DocType Definition
- **Name:** Clarinet Task Depends On
- **Module:** Instrument Setup
- **Autoname:** format:CTDO-{#####}
- **Fields:** 1

#### Fields
- `task` — Link — reqd=1 — label=Task

---

## `doctype/clarinet_task_depends_on/clarinet_task_depends_on.py`
- **Type:** python  
- **Lines:** 27  
- **Size:** 757 bytes  

### Classes
- **L12 — `class ClarinetTaskDependsOn(Document)`**
  - Doc: No class docstring provided.

---

## `doctype/clarinet_template_task/README.md`
- **Type:** markdown  
- **Lines:** 271  
- **Size:** 9865 bytes  

(Markdown file; content summarized.)

---

## `doctype/clarinet_template_task/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `doctype/clarinet_template_task/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 215 bytes  

---

## `doctype/clarinet_template_task/__pycache__/clarinet_template_task.cpython-312.pyc`
- **Type:** other  
- **Lines:** 19  
- **Size:** 1397 bytes  

---

## `doctype/clarinet_template_task/clarinet_template_task.js`
- **Type:** javascript  
- **Lines:** 9  
- **Size:** 178 bytes  

### Scripted behaviors / functions
- `frappe.ui.form.on(Clarinet Template Task)(frm)`

---

## `doctype/clarinet_template_task/clarinet_template_task.json`
- **Type:** json  
- **Lines:** 85  
- **Size:** 2404 bytes  

### DocType Definition
- **Name:** Clarinet Template Task
- **Module:** Instrument Setup
- **Autoname:** format:CTT-{#####}
- **Fields:** 7

#### Fields
- `sequence` — Int — reqd=1 — label=Sequence
- `depends_on` — Table — reqd=0 — label=Depends On
- `subject` — Data — reqd=1 — label=Subject
- `description` — Small Text — reqd=0 — label=Description
- `default_priority` — Select — reqd=0 — label=Priority
- `exp_start_offset_days` — Int — reqd=0 — label=Expected Start Offset (days)
- `exp_duration_mins` — Int — reqd=0 — label=Expected Duration (mins)

---

## `doctype/clarinet_template_task/clarinet_template_task.py`
- **Type:** python  
- **Lines:** 34  
- **Size:** 1195 bytes  

### Classes
- **L12 — `class ClarinetTemplateTask(Document)`**
  - Doc: No class docstring provided.

---

## `doctype/clarinet_template_task_depends_on/README.md`
- **Type:** markdown  
- **Lines:** 165  
- **Size:** 6304 bytes  

(Markdown file; content summarized.)

---

## `doctype/clarinet_template_task_depends_on/__init__.py`
- **Type:** python  
- **Lines:** 6  
- **Size:** 278 bytes  

---

## `doctype/clarinet_template_task_depends_on/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 226 bytes  

---

## `doctype/clarinet_template_task_depends_on/__pycache__/clarinet_template_task_depends_on.cpython-312.pyc`
- **Type:** other  
- **Lines:** 8  
- **Size:** 844 bytes  

---

## `doctype/clarinet_template_task_depends_on/clarinet_template_task_depends_on.json`
- **Type:** json  
- **Lines:** 44  
- **Size:** 1233 bytes  

### DocType Definition
- **Name:** Clarinet Template Task Depends On
- **Module:** Instrument Setup
- **Autoname:** format:CTTDO-{#####}
- **Fields:** 2

#### Fields
- `sequence` — Int — reqd=1 — label=Depends on Sequence
- `subject` — Link — reqd=1 — label=Parent Task's Subject

---

## `doctype/clarinet_template_task_depends_on/clarinet_template_task_depends_on.py`
- **Type:** python  
- **Lines:** 26  
- **Size:** 869 bytes  

### Classes
- **L10 — `class ClarinetTemplateTaskDependsOn(Document)`**
  - Doc: No class docstring provided.

---

## `doctype/setup_checklist_item/README.md`
- **Type:** markdown  
- **Lines:** 347  
- **Size:** 13435 bytes  

(Markdown file; content summarized.)

---

## `doctype/setup_checklist_item/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `doctype/setup_checklist_item/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 213 bytes  

---

## `doctype/setup_checklist_item/__pycache__/setup_checklist_item.cpython-312.pyc`
- **Type:** other  
- **Lines:** 7  
- **Size:** 924 bytes  

---

## `doctype/setup_checklist_item/setup_checklist_item.json`
- **Type:** json  
- **Lines:** 45  
- **Size:** 854 bytes  

### DocType Definition
- **Name:** Setup Checklist Item
- **Module:** Instrument Setup
- **Autoname:** format:SCI-{#####}
- **Fields:** 3

#### Fields
- `task` — Data — reqd=0 — label=Task
- `completed` — Check — reqd=0 — label=Completed
- `notes` — Text — reqd=0 — label=Notes

---

## `doctype/setup_checklist_item/setup_checklist_item.py`
- **Type:** python  
- **Lines:** 26  
- **Size:** 726 bytes  

### Classes
- **L9 — `class SetupChecklistItem(Document)`**
  - Doc: No class docstring provided.

---

## `doctype/setup_material_log/README.md`
- **Type:** markdown  
- **Lines:** 228  
- **Size:** 8499 bytes  

(Markdown file; content summarized.)

---

## `doctype/setup_material_log/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `doctype/setup_material_log/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 211 bytes  

---

## `doctype/setup_material_log/__pycache__/setup_material_log.cpython-312.pyc`
- **Type:** other  
- **Lines:** 14  
- **Size:** 1243 bytes  

---

## `doctype/setup_material_log/setup_material_log.js`
- **Type:** javascript  
- **Lines:** 39  
- **Size:** 1184 bytes  

### Scripted behaviors / functions
- `recalc_amount(cdt, cdn)`
- `frappe.ui.form.on(Setup Material Log)(frm)`

---

## `doctype/setup_material_log/setup_material_log.json`
- **Type:** json  
- **Lines:** 75  
- **Size:** 1871 bytes  

### DocType Definition
- **Name:** Setup Material Log
- **Module:** Instrument Setup
- **Autoname:** N/A
- **Fields:** 6

#### Fields
- `item_code` — Link — reqd=1 — label=Item
- `description` — Small Text — reqd=0 — label=Description
- `qty` — Float — reqd=0 — label=Qty
- `uom` — Link — reqd=0 — label=UOM
- `rate` — Currency — reqd=0 — label=Rate
- `amount` — Currency — reqd=0 — label=Amount

---

## `doctype/setup_material_log/setup_material_log.py`
- **Type:** python  
- **Lines:** 35  
- **Size:** 930 bytes  

### Functions
- **L31 — `validate(self)`**
  - Doc: No docstring provided.

### Classes
- **L11 — `class SetupMaterialLog(Document)`**
  - Doc: No class docstring provided.
  - **Methods:**
    - L31 — `validate(self)` — No method docstring provided.

---

## `doctype/setup_template/README.md`
- **Type:** markdown  
- **Lines:** 304  
- **Size:** 14259 bytes  

(Markdown file; content summarized.)

---

## `doctype/setup_template/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `doctype/setup_template/__pycache__/__init__.cpython-312.pyc`
- **Type:** other  
- **Lines:** 3  
- **Size:** 207 bytes  

---

## `doctype/setup_template/__pycache__/setup_template.cpython-312.pyc`
- **Type:** other  
- **Lines:** 70  
- **Size:** 9243 bytes  

---

## `doctype/setup_template/setup_template.js`
- **Type:** javascript  
- **Lines:** 204  
- **Size:** 7131 bytes  

### Scripted behaviors / functions
- `add_tools(frm)`
- `normalize_sequence(frm)`
- `recalc_totals(frm)`
- `preview_schedule_dialog(frm)`
- `render_preview(rows, setup_date)`
- `nearEq(a, b)`
- `frappe.ui.form.on(Setup Template)(frm)`
- `frappe.ui.form.on(Clarinet Template Task)(frm)`

---

## `doctype/setup_template/setup_template.json`
- **Type:** json  
- **Lines:** 186  
- **Size:** 5501 bytes  

### DocType Definition
- **Name:** Setup Template
- **Module:** Instrument Setup
- **Autoname:** format:SETUP-{clarinet_model}
- **Fields:** 18

#### Fields
- `basic_info_section` — Section Break — reqd=0 — label=Basic Information
- `template_name` — Data — reqd=1 — label=Template Name
- `clarinet_model` — Link — reqd=1 — label=Instrument Model
- `setup_type` — Select — reqd=1 — label=Setup Type
- `column_break_basic` — Column Break — reqd=0 — label=
- `is_active` — Check — reqd=0 — label=Is Active
- `priority` — Select — reqd=0 — label=Default Priority
- `pad_map` — Link — reqd=0 — label=Pad Map
- `estimates_section` — Section Break — reqd=0 — label=Estimates & Defaults
- `estimated_hours` — Float — reqd=0 — label=Estimated Hours
- `estimated_cost` — Currency — reqd=0 — label=Estimated Total Cost
- `column_break_estimates` — Column Break — reqd=0 — label=
- `estimated_materials_cost` — Currency — reqd=0 — label=Estimated Materials Cost
- `default_technician` — Link — reqd=0 — label=Default Technician
- `template_content_section` — Section Break — reqd=0 — label=Template Content
- `default_operations` — Table — reqd=0 — label=Default Operations
- `checklist_items` — Table — reqd=0 — label=Checklist Items
- `template_tasks` — Table — reqd=0 — label=Template Tasks

---

## `doctype/setup_template/setup_template.py`
- **Type:** python  
- **Lines:** 195  
- **Size:** 8219 bytes  

### Functions
- **L26 — `_D(x, default) -> Decimal`**
  - Doc: Safe Decimal parser using str() to avoid binary float artifacts.
- **L35 — `_get_settings_decimal(fieldname, default) -> Decimal`**
  - Doc: Fetch a numeric single value from Repair Portal Settings as Decimal.
- **L43 — `_sum_minutes_and_hours(rows) -> Tuple[int, Decimal]`**
  - Doc: Sum minutes from child rows; if a row lacks minutes (<=0), fall back to legacy exp_duration_days.
Returns (total_minutes_int, hours_decimal_quantized_2dp).
- **L107 — `validate(self)`**
  - Doc: No docstring provided.
- **L119 — `validate_template_consistency(self)`**
  - Doc: No docstring provided.
- **L125 — `auto_create_pad_map(self)`**
  - Doc: No docstring provided.
- **L137 — `validate_template_tasks(self)`**
  - Doc: No docstring provided.
- **L159 — `_compute_total_cost(self, hours) -> Decimal`**
  - Doc: No docstring provided.
- **L168 — `recalc(self) -> dict`**
  - Decorators: `frappe.whitelist()`
  - Doc: Idempotent compute-only endpoint:
- Does NOT mutate the document on the server.
- Returns hours & cost computed from the current child rows + settings.
- **L182 — `get_template_summary(self)`**
  - Decorators: `frappe.whitelist()`
  - Doc: No docstring provided.

### Classes
- **L71 — `class SetupTemplate(Document)`**
  - Doc: No class docstring provided.
  - **Methods:**
    - L107 — `validate(self)` — No method docstring provided.
    - L119 — `validate_template_consistency(self)` — No method docstring provided.
    - L125 — `auto_create_pad_map(self)` — No method docstring provided.
    - L137 — `validate_template_tasks(self)` — No method docstring provided.
    - L159 — `_compute_total_cost(self, hours)` — No method docstring provided.
    - L168 — `recalc(self)` — Idempotent compute-only endpoint:
- Does NOT mutate the document on the server.
- Returns hours & cost computed from the current child rows + settings.
    - L182 — `get_template_summary(self)` — No method docstring provided.

---

## `hooks/after_install/create_a_clarinet_standard_template.py`
- **Type:** python  
- **Lines:** 223  
- **Size:** 14265 bytes  

### Functions
- **L4 — `create_a_clarinet_standard_template()`**
  - Doc: Creates the 'A Clarinet Standard Setup' template based on the specified
DocType structure if it does not already exist.

---

## `hooks/after_install/create_bb_clarinet_standard_template.py`
- **Type:** python  
- **Lines:** 223  
- **Size:** 13061 bytes  

### Functions
- **L4 — `create_bb_clarinet_standard_template()`**
  - Doc: Creates the 'B♭ Clarinet Standard Setup' template based on the new structure
if it does not already exist.

---

## `hooks/after_install/create_eb_clarinet_standard_template.py`
- **Type:** python  
- **Lines:** 223  
- **Size:** 14335 bytes  

### Functions
- **L4 — `create_eb_clarinet_standard_template()`**
  - Doc: Creates the 'E♭ Clarinet Standard Setup' template based on the specified
DocType structure if it does not already exist.

---

## `hooks/load_templates.py`
- **Type:** python  
- **Lines:** 78  
- **Size:** 2934 bytes  

### Functions
- **L14 — `load_setup_templates()`**
  - Doc: Load all Setup Template JSON files from the instrument_setup/hooks/templates directory
and insert/update them into the Frappe database.

This function is intended to be hooked into `after_install` in hooks.py.

---

## `hooks/templates/brand_bundled.json`
- **Type:** json  
- **Lines:** 23  
- **Size:** 508 bytes  

(JSON parsed but not a dict top-level.)

---

## `hooks/templates/create_a_clarinet_standard_template.json`
- **Type:** json  
- **Lines:** 43  
- **Size:** 8268 bytes  

---

## `hooks/templates/create_bb_clarinet_standard_template.json`
- **Type:** json  
- **Lines:** 166  
- **Size:** 7836 bytes  

---

## `hooks/templates/instrument_model_import.json`
- **Type:** json  
- **Lines:** 82  
- **Size:** 2288 bytes  

(JSON parsed but not a dict top-level.)

---

## `print_format/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `print_format/clarinet_setup_certificate/README.md`
- **Type:** markdown  
- **Lines:** 21  
- **Size:** 743 bytes  

(Markdown file; content summarized.)

---

## `print_format/clarinet_setup_certificate/__init__.py`
- **Type:** python  
- **Lines:** 1  
- **Size:** 0 bytes  

---

## `print_format/clarinet_setup_certificate/clarinet_setup_certificate.html`
- **Type:** html  
- **Lines:** 357  
- **Size:** 14170 bytes  

---

## `print_format/clarinet_setup_certificate/clarinet_setup_certificate.json`
- **Type:** json  
- **Lines:** 33  
- **Size:** 1538 bytes  

---

## `report/parts_consumption/parts_consumption.json`
- **Type:** json  
- **Lines:** 11  
- **Size:** 311 bytes  

---

## `report/parts_consumption/parts_consumption.py`
- **Type:** python  
- **Lines:** 23  
- **Size:** 546 bytes  

### Functions
- **L4 — `execute(filters)`**
  - Doc: No docstring provided.

---

## `report/technician_performance/technician_performance.json`
- **Type:** json  
- **Lines:** 11  
- **Size:** 321 bytes  

---

## `report/technician_performance/technician_performance.py`
- **Type:** python  
- **Lines:** 32  
- **Size:** 880 bytes  

### Functions
- **L4 — `execute(filters)`**
  - Doc: No docstring provided.

---

## `report/turnaround_time_analysis/turnaround_time_analysis.json`
- **Type:** json  
- **Lines:** 28  
- **Size:** 534 bytes  

---

## `report/turnaround_time_analysis/turnaround_time_analysis.sql`
- **Type:** other  
- **Lines:** 12  
- **Size:** 302 bytes  

---

## `web_form/repair_status/repair_status.json`
- **Type:** json  
- **Lines:** 32  
- **Size:** 588 bytes  

---

## Issues & Quality Notes (Auto-scan)

### Python Functions Missing Docstrings
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/report/parts_consumption/parts_consumption.py` — `execute` (L4)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/report/technician_performance/technician_performance.py` — `execute` (L4)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_material_log/setup_material_log.py` — `validate` (L31)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py` — `_normalize_title` (L57)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py` — `validate` (L189)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py` — `_populate_soprano` (L275)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py` — `_populate_bass` (L293)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py` — `_populate_and_enforce` (L367)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py` — `_normalize` (L332)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py` — `_apply` (L339)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.py` — `validate` (L107)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.py` — `validate_template_consistency` (L119)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.py` — `auto_create_pad_map` (L125)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.py` — `validate_template_tasks` (L137)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.py` — `_compute_total_cost` (L159)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.py` — `get_template_summary` (L182)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py` — `update_parent_progress` (L359)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py` — `before_insert` (L104)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py` — `validate` (L110)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py` — `on_submit` (L121)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py` — `ensure_checklist` (L206)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.py` — `validate` (L48)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.py` — `on_update` (L76)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.py` — `on_trash` (L89)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/config/desktop.py` — `get_data` (L9)

### Python Classes Missing Docstrings
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_material_log/setup_material_log.py` — `class SetupMaterialLog` (L11)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_template_task_depends_on/clarinet_template_task_depends_on.py` — `class ClarinetTemplateTaskDependsOn` (L10)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.py` — `class ClarinetPadMap` (L162)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.py` — `class SetupTemplate` (L71)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_operation/clarinet_setup_operation.py` — `class ClarinetSetupOperation` (L9)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_checklist_item/setup_checklist_item.py` — `class SetupChecklistItem` (L9)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py` — `class ClarinetInitialSetup` (L58)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_log/clarinet_setup_log.py` — `class ClarinetSetupLog` (L9)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.py` — `class ClarinetSetupTask` (L14)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_entry/clarinet_pad_entry.py` — `class ClarinetPadEntry` (L11)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_template_task/clarinet_template_task.py` — `class ClarinetTemplateTask` (L12)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_task_depends_on/clarinet_task_depends_on.py` — `class ClarinetTaskDependsOn` (L12)

### JSON Files With Parse Errors
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/.vscode/extensions.json` — Expecting property name enclosed in double quotes: line 2 column 2 (char 3)

### JavaScript Functions Detected (quick scan)
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_material_log/setup_material_log.js` — `recalc_amount`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.js` — `looks_like_bass`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.js` — `should_autopopulate`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_pad_map/clarinet_pad_map.js` — `call_server_populate`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.js` — `add_tools`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.js` — `normalize_sequence`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.js` — `recalc_totals`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.js` — `preview_schedule_dialog`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.js` — `render_preview`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/setup_template/setup_template.js` — `nearEq`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `apply_setup_template`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `set_headline`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `show_progress`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `show_project_timeline`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `calculate_expected_end_date`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `calculate_estimated_costs`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `update_status_indicators`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `add_draft_buttons`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `add_nav_buttons`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `add_certificate_button`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js` — `ensure_saved`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.js` — `show_status_banner`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.js` — `add_status_buttons`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.js` — `set_status`
- `/home/frappe/frappe-bench/apps/repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task.js` — `show_dependency_summary`
