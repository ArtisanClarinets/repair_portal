# Instrument Profile Module

## Last Updated: 2025-06-15

## Overview

The Instrument Profile module provides a unified record for each instrument (e.g., clarinet), consolidating all relevant history, repair logs, service events, parts, and attached documentation. This master record connects to the repair_logging module for all activity and ensures a complete 360° view of an instrument's lifecycle in the MRW Artisan Instruments Repair Portal.

---

## Recent Updates (2025-06-15)
- **Refactored Instrument Profile DocType** for pure master-data use (brand, model, serial, owner, photo, etc.)
- **Serial number** is now enforced as globally unique per instrument
- **last_service_date** is updated automatically based on linked service logs in the repair_logging module
- **Removed any repair-event or status-specific fields** from Instrument Profile; all logs/repairs are now managed centrally via service_log and clarinet_repair_log in repair_logging
- **Updated server-side controller** to ensure serial uniqueness and to auto-update last_service_date when service events are created/updated
- **Docs reviewed and structure validated for production-readiness**

## Key File Paths
- DocType: `/opt/frappe/erp-bench/apps/repair_portal/repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.json`
- Controller: `/opt/frappe/erp-bench/apps/repair_portal/repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py`

## Next Steps
- Update Desk dashboard to show all linked Service Logs for each Instrument Profile
- Integrate timeline/history, parts, and attachments via workspace/dashboard config

---

## Usage
- All instrument-specific data is maintained on Instrument Profile
- All service, repair, and logging events are managed in repair_logging and are linked back to Instrument Profile by Link field
- last_service_date auto-syncs based on linked service logs

---
