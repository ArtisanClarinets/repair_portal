# Repair Portal

## Overview
The Repair Portal is a modular Frappe application built for clarinet service management at MRW Artisan Instruments. It includes everything from intake, inspection, planning, and repair to final QA and upgrades.

## Modules
- **Intake**: Customer and instrument intake documentation.
- **Inspection**: Damage and condition evaluations.
- **Service Planning**: Organize tasks and priorities.
- **Repair Logging**: Track repair operations.
- **Quality Assurance**: Checklist-driven evaluations.
- **Tools**: Calibration and maintenance of workshop tools.
- **Enhancements**: Customer-driven upgrade requests.

## Features
- Workflow for intake approvals
- Client-side scripting for automation
- Workspace UI per module
- Test cases and fixtures for CI/CD
- Dashboard shortcuts for rapid navigation

## Developer Info
- Activate env: `source /opt/frappe/venv/bin/activate`
- Migrate: `cd /opt/frappe/erpnext-bench && bench migrate`
- Export fixtures: `bench export-fixtures`

## Tests
Run via:
```bash
cd /opt/frappe/erpnext-bench
bench --site yoursite test --module repair_portal
```