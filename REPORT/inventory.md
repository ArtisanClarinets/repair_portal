# Inventory Report for repair_portal

**Date:** July 30, 2025

## 1. App & Framework Versions

- **Frappe:** 15.74.2
- **ERPNext:** 15.71.1
- **repair_portal:** 0.0.1 (branch: main)
- **Other apps:** doppio, payments, bench_tools
- **OS:** Linux

## 2. Backend File Tree Overview

The backend file tree has been grouped based on functionality and module type. Below is a high-level summary:

### API Modules & Controllers

- **/repair_portal/api/**: Contains core API controllers such as:
  - `clarinet_utils.py`
  - `client_portal.py`
  - `customer.py`
  - `intake_dashboard.py`
  - `technician_dashboard.py`

- Additional controllers are distributed across modules in subdirectories (e.g., customer, intake, instrument_setup, inspection, instrument_profile, player_profile).

### DocType Directories

Key DocType directories include:

- **customer/doctype/**: Contains DocTypes related to customer consent, consent forms, and customer workflows.
- **intake/doctype/clarinet_intake/**: Manages the instrument intake process.
- **instrument_setup/doctype/clarinet_initial_setup/**: Handles instrument setup processes.
- **instrument_setup/doctype/setup_template/**: Contains setup templates.
- **inspection/doctype/instrument_inspection/**: Manages inspection procedures.
- **instrument_profile/doctype/**: Includes DocTypes for instrument and instrument profile management.
- **instrument_setup/doctype/clarinet_pad_map/**: Manages pad mapping for instruments.
- **player_profile/doctype/player_profile/**: Contains DocTypes for managing player profiles.

### Hooks & Configuration

- **Hooks:**
  - The main `hooks.py` file integrates custom workflows using doc_events and scheduler_events. Preliminary review of the first 200 lines indicates standard use of hooks; detailed static analysis will follow in Phase 2.
- **Configuration:**
  - Files such as `config/desktop.py` set up desktop icons and module visibility.

### Tests

- Tests are available in various locations:
  - `/repair_portal/tests/`
  - `/instrument_setup/test/`
  - Additional tests scattered in module-specific directories.

### Patches & Migrations

- The presence of `patches.txt` and scripts under `/repair_portal/scripts/` suggest historical migrations and ad-hoc patches have been applied.

## 3. Hooks Summary

- The `hooks.py` file registers multiple document event handlers and scheduler events. A detailed review will be conducted to verify that the handlers are lightweight, properly secured, and compliant with Frappe best practices.

## 4. Additional Notes

- No `fixtures/` or `workspace/` directories were found in the package root.
- The current file inventory confirms that all expected backend modules are in place.
- Further static analysis will focus on DocType JSON integrity, permissions, indexing, and API security in Phase 2.

---

*This inventory report forms the baseline for the upcoming security and integrity assessments, and all findings are to be referenced against Frappe v15 best practices.*
