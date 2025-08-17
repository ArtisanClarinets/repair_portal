# Repair Portal

Comprehensive documentation for the `repair_portal` Frappe app: modules, doctypes, dev flow, and conventions.

## Overview
- Domain app for instrument repair workflows: intake → inspection → setup → repair logging → QA → delivery.
- Built on Frappe/ERPNext; includes backend DocTypes with Python controllers and optional client scripts.

## Tech Stack
- Backend: Python 3.10, Frappe framework
- Frontend: Vanilla JS/Vue where needed, assets under `repair_portal/public`
- Tooling: Ruff, Flake8, Biome, ESLint, Pre-commit

## Installation
```bash
bench get-app local path/to/repair_portal  # or add as app in bench
bench --site <site> install-app repair_portal
bench --site <site> migrate
```

## Development
```bash
bench start                                 # run dev server
bench --site <site> clear-cache             # after schema/code changes
bench --site <site> run-tests --app repair_portal
npm run lint:backend && npm run lint:frontend
pre-commit run -a
```

## Project Structure
```
repair_portal/
  <module>/
    doctype/<doctype>/<doctype>.(py|js|json)
    report/, page/, config/, ...
public/ (assets)
```

## Modules and DocTypes
### Inspection
- Path: `repair_portal/inspection`
- DocTypes:
  - `instrument_inspection` (py,js)

### Intake
- Path: `repair_portal/intake`
- DocTypes:
  - `brand_mapping_rule` (py)
  - `clarinet_intake` (py,js)
  - `clarinet_intake_settings` (py)
  - `intake_accessory_item` (py)
  - `loaner_instrument` (py)
  - `loaner_return_check` (py)

### Instrument Setup
- Path: `repair_portal/instrument_setup`
- DocTypes:
  - `clarinet_initial_setup` (py,js)
  - `clarinet_pad_entry` (py)
  - `clarinet_pad_map` (py,js)
  - `clarinet_setup_log` (py,js)
  - `clarinet_setup_operation` (py)
  - `clarinet_setup_task` (py,js)
  - `clarinet_task_depends_on` (py,js)
  - `clarinet_template_task` (py,js)
  - `clarinet_template_task_depends_on` (py)
  - `setup_checklist_item` (py)
  - `setup_material_log` (py,js)
  - `setup_template` (py,js)

### QA
- Path: `repair_portal/qa`
- DocTypes:
  - `final_qa_checklist` (py)
  - `final_qa_checklist_item` (py)

### Repair Logging
- Path: `repair_portal/repair_logging`
- DocTypes:
  - `barcode_scan_entry` (py)
  - `diagnostic_metrics` (py)
  - `instrument_interaction_log` (py)
  - `key_measurement` (py)
  - `material_use_log` (py)
  - `pad_condition` (py)
  - `related_instrument_interaction` (py)
  - `repair_parts_used` (py)
  - `repair_task_log` (py)
  - `tenon_measurement` (py)
  - `tone_hole_inspection_record` (py,js)
  - `tool_usage_log` (py)
  - `visual_inspection` (py)
  - `warranty_modification_log` (py)

### Repair Portal
- Path: `repair_portal/repair_portal`
- DocTypes:
  - `pulse_update` (py)
  - `qa_checklist_item` (py)
  - `technician` (py,js)

### Service Planning
- Path: `repair_portal/service_planning`
- DocTypes:
  - `estimate_line_item` (py)
  - `repair_estimate` (py)
  - `service_plan` (py)
  - `service_task` (py)
  - `tasks` (py)

### Tools
- Path: `repair_portal/tools`
- DocTypes:
  - `tool` (py)
  - `tool_calibration_log` (py)

### Enhancements
- Path: `repair_portal/enhancements`
- DocTypes:
  - `customer_upgrade_request` (py)
  - `upgrade_option` (py)

### Instrument Profile
- Path: `repair_portal/instrument_profile`
- DocTypes:
  - `client_instrument_profile` (py,js)
  - `customer_external_work_log` (py,js)
  - `instrument` (py,js)
  - `instrument_accessory` (py)
  - `instrument_category` (py,js)
  - `instrument_condition_record` (py)
  - `instrument_model` (py,js)
  - `instrument_photo` (py)
  - `instrument_profile` (py,js)
  - `instrument_serial_number` (py,js)

### Repair
- Path: `repair_portal/repair`
- DocTypes:
  - `default_operations` (py,js)
  - `operation_template` (py)
  - `pulse_update` (py)
  - `repair_feedback` (py)
  - `repair_issue` (py)
  - `repair_order` (py,js)
  - `repair_request` (py,js)
  - `repair_task` (py)

### Lab
- Path: `repair_portal/lab`
- DocTypes:
  - `environment_log` (py)
  - `measurement_entry` (py)
  - `measurement_session` (py)

## Testing
- Uses Frappe test runner with `unittest`. Name tests `test_*.py` and scope fixtures to each test.
- Example sites are not required; tests create their own documents and clean up.

## Coding Standards
- Tabs for indentation; 110 char lines. Run `ruff format` / `ruff check` and Biome/ESLint for JS.
- Follow Frappe DocType conventions; do not edit generated JSON manually.

## Contributing
- Use Conventional Commits (e.g., `feat(instrument_setup): add task deps`).
- Open PRs with description, migration notes, and tests where applicable.