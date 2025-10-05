# Operations & Quality Checklist

## Background Jobs
- **Configured Jobs**: None registered under `scheduler_events`; warranty cron module exists but is not scheduled.【F:repair_portal/hooks.py†L21-L121】【F:repair_portal/instrument_profile/cron/warranty_expiry_check.py†L1-L120】
- **Action**: Define hourly/daily scheduler events for warranty checks, SLA audits, and notification digests. Ensure jobs log to dedicated logger and notify admins on failure.

## Notifications & Alerts
- **Configured**: Instrument profile notifications (status change, missing customer/player).【F:repair_portal/instrument_profile/notification/instrument_status_change/instrument_status_change.json†L1-L40】
- **Gaps**: Intake/repair/QA stages lack notifications; warranty cron does not emit alerts; customer approvals not wired to email/SMS.

## Print Formats & Labels
- **Existing**: Instrument profile print formats (QR tag, summary).【F:repair_portal/instrument_profile/print_format/instrument_qr_tag/instrument_qr_tag.json†L1-L9】
- **Missing**: Repair order job tags with barcodes/QR codes, technician work orders, intake labels aligned with blueprint.

## Workspaces & Dashboards
- **Modules**: Desktop entries for all modules (Intake, Repair, Instrument Setup, etc.).【F:repair_portal/config/desktop.py†L4-L78】
- **Dashboards**: Technician dashboard page provides task overview; lab console for diagnostics.【F:repair_portal/inspection/page/technician_dashboard/technician_dashboard.js†L1-L160】【F:repair_portal/lab/page/lab_console/lab_console.js†L1-L160】
- **Gaps**: No executive dashboards for SLA, revenue vs cost, or capacity utilization.

## Fixtures & Defaults
- **Fixtures**: No exported `fixtures` directory; relies on install hooks to seed consent artifacts and DocTypes.【F:repair_portal/hooks.py†L21-L121】
- **Defaults**: `Repair Settings` single DocType stores default company/warehouse/labor rate.【F:repair_portal/repair_portal_settings/doctype/repair_settings/repair_settings.json†L1-L48】

## Logging & Metrics
- **Implemented**: Lab API logs errors; warranty cron prepared with logger usage (not scheduled).【F:repair_portal/lab/api.py†L28-L135】【F:repair_portal/instrument_profile/cron/warranty_expiry_check.py†L20-L96】
- **Gaps**: No centralized metrics dashboard or error alerting pipeline; SLA/performance metrics not aggregated.

## Deployment Notes
- Requires ERPNext dependencies (`frappe`, `erpnext`) and optional CV/ReportLab libs for pad count intake.【F:repair_portal/inventory/doctype/pad_count_intake/pad_count_intake.py†L1-L120】
- After install, hooks call `reload_all_doctypes`, seed consent artifacts—monitor for long migrations.【F:repair_portal/hooks.py†L21-L45】
- Recommended to run `python scripts/schema_guard.py` pre/post deploy as referenced in repo tooling.
