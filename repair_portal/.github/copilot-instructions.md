# Fortune‑500 Engineering Guide

**Project**: `repair_portal`
**Stack**: Frappe v15 • ERPNext v15 • MariaDB • Vue/React (Tailwind + shadcn/ui) • frappe-bench CLI
**Root Path**: `/opt/frappe/erp-bench/apps/repair_portal/`

---

## 1 · Executive Snapshot

Welcome to *repair_portal*, the digital workshop where artisan clarinets meet Fortune‑500 discipline.
Your mission is simple: ship secure, production‑ready features—no half measures.

---

## 2 · Directory & Module Map

```
├── biome.json
├── CHANGELOG.md
├── customer_refactor.txt
├── cypress.config.js
├── DEV_LOGIC_SUMMARY.md
├── documentation
│   ├── DASHBOARD_CHARTS.md
│   ├── DOCTYPE.md
│   ├── REPORT.md
│   ├── WORKFLOW.md
│   └── WORKSPACE.md
├── eslint.config.js
├── filelist.txt
├── license.txt
├── modules.txt
├── package.json
├── package-lock.json
├── pyproject.toml
├── README.md
├── repair_portal
│   ├── api
│   │   ├── clarinet_utils.py
│   │   ├── client_portal.py
│   │   ├── customer.py
│   │   ├── intake_dashboard.py
│   │   └── technician_dashboard.py
│   ├── api.py
│   ├── config
│   │   ├── desktop.py
│   │   ├── __init__.py
│   │   └── workspace_sort_map.json
│   ├── controller_review.md
│   ├── customer
│   │   ├── CHANGELOG.md
│   │   ├── dashboard
│   │   │   ├── client_profile_dashboard
│   │   │   └── customer_dashboard
│   │   │       ├── customer_dashboard.json
│   │   │       └── customer_dashboard.py
│   │   ├── doctype
│   │   │   ├── consent_log
│   │   │   │   ├── consent_log.json
│   │   │   │   └── consent_log.py
│   │   │   ├── consent_log_entry
│   │   │   │   ├── consent_log_entry.json
│   │   │   │   └── consent_log_entry.py
│   │   │   ├── customer_type
│   │   │   │   ├── customer_type.json
│   │   │   │   ├── customer_type.py
│   │   │   │   └── __init__.py
│   │   │   ├── __init__.py
│   │   │   ├── instruments_owned
│   │   │   │   ├── instruments_owned.json
│   │   │   │   └── instruments_owned.py
│   │   │   └── linked_players
│   │   │       ├── __init__.py
│   │   │       ├── linked_players.js
│   │   │       ├── linked_players.json
│   │   │       └── linked_players.py
│   │   ├── events
│   │   │   └── utils.py
│   │   ├── __init__.py
│   │   ├── module_health.md
│   │   ├── notification
│   │   │   └── draft_customer.json
│   │   ├── page
│   │   │   ├── client_portal
│   │   │   │   ├── client_portal.js
│   │   │   │   ├── client_portal.json
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── technical_debt.md
│   │   ├── workflow
│   │   │   └── client_profile_workflow
│   │   │       └── client_profile_workflow.json
│   │   ├── workflow_action_master
│   │   │   ├── workflow_action_master
│   │   │   │   └── workflow_action_master.json
│   │   │   └── workflow_action_master.py
│   │   └── workflow_state
│   │       ├── active
│   │       │   └── active.json
│   │       ├── archived
│   │       │   └── archived.json
│   │       ├── deleted
│   │       │   └── deleted.json
│   │       ├── draft
│   │       │   └── draft.json
│   │       └── workflow_state.py
│   ├── customer_refactor.txt
│   ├── DEV_LOGIC_SUMMARY.md
│   ├── docs
│   │   ├── customer_autocreate_setup.md
│   │   ├── JS_API.MD
│   │   ├── new_instrument_intake.md
│   │   └── PYTHON_API.md
│   ├── enhancements
│   │   ├── config
│   │   │   └── desktop.py
│   │   ├── custom_script
│   │   │   └── customer_upgrade_request.json
│   │   ├── dashboard_chart
│   │   │   └── upgrade_requests_over_time.json
│   │   ├── doctype
│   │   │   ├── customer_upgrade_request
│   │   │   │   ├── customer_upgrade_request.json
│   │   │   │   └── customer_upgrade_request.py
│   │   │   └── upgrade_option
│   │   │       ├── upgrade_option.json
│   │   │       └── upgrade_option.py
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── report
│   │       ├── top_upgrade_requests
│   │       │   ├── top_upgrade_requests.json
│   │       │   └── top_upgrade_requests.py
│   │       └── upgrade_conversion_rates
│   │           ├── upgrade_conversion_rates.json
│   │           └── upgrade_conversion_rates.py
│   ├── hooks.py
│   ├── __init__.py
│   ├── inspection
│   │   ├── config
│   │   │   ├── desktop.py
│   │   │   ├── docs.py
│   │   │   └── __init__.py
│   │   ├── doctype
│   │   │   ├── __init__.py
│   │   │   └── instrument_inspection
│   │   │       ├── instrument_inspection.js
│   │   │       ├── instrument_inspection.json
│   │   │       └── instrument_inspection.py
│   │   ├── __init__.py
│   │   ├── migrate_clarinet_inspection_to_report.py
│   │   ├── modules.txt
│   │   ├── page
│   │   │   ├── __init__.py
│   │   │   └── technician_dashboard
│   │   │       ├── __init__.py
│   │   │       ├── technician_dashboard.js
│   │   │       └── technician_dashboard.json
│   │   ├── README.md
│   │   └── workflow
│   │       └── inspection_report_workflow.json
│   ├── instrument_profile
│   │   ├── config
│   │   │   ├── desktop.py
│   │   │   └── __init__.py
│   │   ├── cron
│   │   │   └── warranty_expiry_check.py
│   │   ├── custom_script
│   │   │   └── instrument_profile_auto_status.json
│   │   ├── dashboard
│   │   │   └── instrument_profile_dashboard
│   │   ├── dashboard_chart
│   │   │   ├── instrument_status_distribution
│   │   │   │   └── instrument_status_distribution.json
│   │   │   └── warranty_distribution
│   │   │       └── warranty_distribution.json
│   │   ├── doctype
│   │   │   ├── clarinet_repair_log
│   │   │   │   ├── clarinet_repair_log.py
│   │   │   │   └── __init__.py
│   │   │   ├── client_instrument_profile
│   │   │   │   ├── client_instrument_profile.json
│   │   │   │   └── client_instrument_profile.py
│   │   │   ├── consent_log
│   │   │   │   └── consent_log.py
│   │   │   ├── consent_log_entry
│   │   │   │   ├── consent_log_entry.json
│   │   │   │   ├── consent_log_entry.py
│   │   │   │   └── __init__.py
│   │   │   ├── customer_external_work_log
│   │   │   │   ├── customer_external_work_log.json
│   │   │   │   └── customer_external_work_log.py
│   │   │   ├── document_history
│   │   │   │   ├── document_history.json
│   │   │   │   ├── document_history.py
│   │   │   │   └── __init__.py
│   │   │   ├── external_work_logs
│   │   │   │   ├── external_work_logs.json
│   │   │   │   └── external_work_logs.py
│   │   │   ├── __init__.py
│   │   │   ├── instrument
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instrument.js
│   │   │   │   ├── instrument.json
│   │   │   │   ├── instrument.py
│   │   │   │   └── test_instrument.py
│   │   │   ├── instrument_condition_record
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instrument_condition_record.json
│   │   │   │   ├── instrument_condition_record.py
│   │   │   │   ├── instrument_condition_record_workflow.json
│   │   │   │   └── test_instrument_condition_record.py
│   │   │   ├── instrument_document_history
│   │   │   │   ├── instrument_document_history.json
│   │   │   │   ├── instrument_document_history.py
│   │   │   │   └── README.md
│   │   │   ├── instrument_intake_batch
│   │   │   │   ├── instrument_intake_batch.json
│   │   │   │   └── instrument_intake_batch.py
│   │   │   ├── instrument_profile
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instrument_profile.js
│   │   │   │   ├── instrument_profile.json
│   │   │   │   ├── instrument_profile_list.js
│   │   │   │   ├── instrument_profile.py
│   │   │   │   └── README.md
│   │   │   ├── instrument_tracker
│   │   │   │   └── instrument_tracker.py
│   │   │   └── intake_entry
│   │   │       ├── __init__.py
│   │   │       ├── intake_entry.json
│   │   │       └── intake_entry.py
│   │   ├── events
│   │   │   ├── __init__.py
│   │   │   └── utils.py
│   │   ├── __init__.py
│   │   ├── list_dashboard
│   │   │   ├── instrument_profile
│   │   │   └── instrument_profile_dashboard
│   │   ├── module_def
│   │   │   └── instrument_profile.json
│   │   ├── notification
│   │   │   ├── instrument_status_change
│   │   │   │   └── instrument_status_change.json
│   │   │   ├── missing_customer
│   │   │   │   └── missing_customer.json
│   │   │   └── missing_player_profile
│   │   │       └── missing_player_profile.json
│   │   ├── print_format
│   │   │   ├── instrument_profile_qr
│   │   │   │   └── instrument_profile_qr.json
│   │   │   ├── instrument_profile_summary
│   │   │   │   └── instrument_profile_summary.json
│   │   │   ├── instrument_summary
│   │   │   │   └── instrument_summary.json
│   │   │   └── instrument_tag
│   │   │       └── instrument_tag.json
│   │   ├── README.md
│   │   ├── report
│   │   │   ├── instrument_inventory_report
│   │   │   │   ├── instrument_inventory_report.json
│   │   │   │   └── instrument_inventory_report.py
│   │   │   ├── instrument_profile_report
│   │   │   │   ├── instrument_profile_report.json
│   │   │   │   └── instrument_profile_report.py
│   │   │   ├── instrument_service_history
│   │   │   │   ├── instrument_service_history.json
│   │   │   │   └── instrument_service_history.py
│   │   │   ├── pending_client_instruments
│   │   │   │   ├── pending_client_instruments.json
│   │   │   │   └── pending_client_instruments.py
│   │   │   └── warranty_status_report
│   │   │       ├── warranty_status_report.json
│   │   │       └── warranty_status_report.py
│   │   ├── web_form
│   │   │   ├── client_instrument_profile
│   │   │   │   └── client_instrument_profile.json
│   │   │   ├── __init__.py
│   │   │   ├── instrument_intake_batch
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instrument_intake_batch.js
│   │   │   │   ├── instrument_intake_batch.json
│   │   │   │   └── instrument_intake_batch.py
│   │   │   └── instrument_registration
│   │   │       ├── __init__.py
│   │   │       ├── instrument_registration.js
│   │   │       ├── instrument_registration.json
│   │   │       └── instrument_registration.py
│   │   ├── workflow
│   │   │   ├── instrument_profile_setup
│   │   │   │   └── instrument_profile_setup.json
│   │   │   ├── instrument_profile_workflow
│   │   │   │   └── instrument_profile_workflow.json
│   │   │   └── instrument_profile_workflow.json
│   │   └── workflow_state
│   │       ├── archived
│   │       │   └── archived.json
│   │       ├── closed
│   │       │   └── closed.json
│   │       ├── delivered
│   │       │   └── delivered.json
│   │       ├── draft
│   │       │   └── draft.json
│   │       ├── in_progress
│   │       │   └── in_progress.json
│   │       ├── open
│   │       │   └── open.json
│   │       ├── ready_for_use
│   │       │   └── ready_for_use.json
│   │       ├── resolved
│   │       │   └── resolved.json
│   │       ├── waiting_on_client
│   │       │   └── waiting_on_client.json
│   │       └── waiting_on_player
│   │           └── waiting_on_player.json
│   ├── instrument_setup
│   │   ├── config
│   │   │   └── desktop.py
│   │   ├── dashboard
│   │   │   └── repairs_dashboard.json
│   │   ├── dashboard_chart
│   │   │   ├── common_inspection_findings.json
│   │   │   └── repairs_by_status.json
│   │   ├── doctype
│   │   │   ├── clarinet_initial_setup
│   │   │   │   ├── clarinet_initial_setup.js
│   │   │   │   ├── clarinet_initial_setup.json
│   │   │   │   └── clarinet_initial_setup.py
│   │   │   ├── clarinet_setup_log
│   │   │   │   ├── clarinet_setup_log.json
│   │   │   │   └── clarinet_setup_log.py
│   │   │   ├── clarinet_setup_operation
│   │   │   │   ├── clarinet_setup_operation.json
│   │   │   │   ├── clarinet_setup_operation.py
│   │   │   │   └── __init__.py
│   │   │   ├── consent_log_entry
│   │   │   │   ├── consent_log_entry.json
│   │   │   │   └── consent_log_entry.py
│   │   │   ├── __init__.py
│   │   │   ├── inspection_finding
│   │   │   │   ├── inspection_finding.json
│   │   │   │   └── inspection_finding.py
│   │   │   ├── material_usage
│   │   │   │   ├── material_usage.json
│   │   │   │   └── material_usage.py
│   │   │   ├── setup_checklist_item
│   │   │   │   ├── setup_checklist_item.json
│   │   │   │   └── setup_checklist_item.py
│   │   │   └── setup_template
│   │   │       ├── __init__.py
│   │   │       ├── setup_template.js
│   │   │       ├── setup_template.json
│   │   │       ├── setup_template.py
│   │   │       └── test_setup_template.py
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── report
│   │   │   ├── parts_consumption
│   │   │   │   ├── parts_consumption.json
│   │   │   │   └── parts_consumption.py
│   │   │   ├── technician_performance
│   │   │   │   ├── technician_performance.json
│   │   │   │   └── technician_performance.py
│   │   │   └── turnaround_time_analysis
│   │   │       ├── turnaround_time_analysis.json
│   │   │       └── turnaround_time_analysis.sql
│   │   ├── test
│   │   │   ├── __init__.py
│   │   │   ├── test_automation_and_kpi.py
│   │   │   ├── test_clarinet_initial_setup.py
│   │   │   └── test_clarinet_initial_setup_refactored.py
│   │   └── web_form
│   │       └── repair_status
│   │           └── repair_status.json
│   ├── intake
│   │   ├── config
│   │   │   └── desktop.py
│   │   ├── dashboard_chart
│   │   │   ├── appointments_by_week.json
│   │   │   ├── avg_intake_to_repair_time.json
│   │   │   ├── intakes_due_soon.json
│   │   │   ├── loaners_checked_out
│   │   │   │   └── loaners_checked_out.json
│   │   │   └── overdue_intakes.json
│   │   ├── doctype
│   │   │   ├── clarinet_intake
│   │   │   │   ├── clarinet_intake.js
│   │   │   │   ├── clarinet_intake.json
│   │   │   │   ├── clarinet_intake.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── README.md
│   │   │   │   ├── test_clarinet_intake.py
│   │   │   │   └── tests
│   │   │   │       └── test_inventory_intake.py
│   │   │   ├── consent_form_template
│   │   │   │   ├── consent_form_template.py
│   │   │   │   ├── consent_form_template.txt
│   │   │   │   └── __init__.py
│   │   │   ├── customer_consent_form
│   │   │   │   ├── customer_consent_form.json
│   │   │   │   └── customer_consent_form.py
│   │   │   ├── __init__.py
│   │   │   ├── intake_accessory_item
│   │   │   │   ├── __init__.py
│   │   │   │   ├── intake_accessory_item.json
│   │   │   │   └── intake_accessory_item.py
│   │   │   ├── intake_checklist_item
│   │   │   │   ├── intake_checklist_item.json
│   │   │   │   └── intake_checklist_item.py
│   │   │   ├── loaner_instrument
│   │   │   │   ├── __init__.py
│   │   │   │   ├── loaner_instrument.json
│   │   │   │   └── loaner_instrument.py
│   │   │   └── loaner_return_check
│   │   │       ├── __init__.py
│   │   │       ├── loaner_return_check.json
│   │   │       └── loaner_return_check.py
│   │   ├── __init__.py
│   │   ├── print_format
│   │   │   └── intake_receipt.json
│   │   ├── README.md
│   │   ├── report
│   │   │   ├── deposit_balance_aging
│   │   │   │   ├── deposit_balance_aging.json
│   │   │   │   └── deposit_balance_aging.py
│   │   │   ├── followup_compliance
│   │   │   │   ├── followup_compliance.json
│   │   │   │   └── followup_compliance.py
│   │   │   ├── intake_by_day
│   │   │   │   ├── intake_by_day.json
│   │   │   │   └── intake_by_day.py
│   │   │   ├── loaner_return_flags
│   │   │   │   ├── loaner_return_flags.json
│   │   │   │   └── loaner_return_flags.py
│   │   │   ├── loaners_outstanding
│   │   │   │   ├── loaners_outstanding.json
│   │   │   │   └── loaners_outstanding.py
│   │   │   ├── loaner_turnover
│   │   │   │   ├── loaner_turnover.json
│   │   │   │   └── loaner_turnover.py
│   │   │   └── upcoming_appointments
│   │   │       ├── upcoming_appointments.json
│   │   │       └── upcoming_appointments.py
│   │   ├── services
│   │   │   └── intake_sync.py
│   │   ├── templates
│   │   │   └── loaner_agreement_template.html
│   │   ├── test
│   │   │   ├── test_clarinet_intake.py
│   │   │   ├── test_intake_workflow_transitions.py
│   │   │   └── test_inventory_intake_flow.py
│   │   ├── utils
│   │   │   └── emailer.py
│   │   ├── web_form
│   │   │   └── clarinet_intake_request
│   │   │       └── clarinet_intake_request.json
│   │   ├── workflow
│   │   │   ├── appointment_workflow.json
│   │   │   ├── clarinet_intake_workflow
│   │   │   │   └── clarinet_intake_workflow.json
│   │   │   └── loaner_return_check_workflow
│   │   │       └── loaner_return_check_workflow.json
│   │   ├── workflow_state
│   │   │   ├── awaiting_customer_approval
│   │   │   │   └── awaiting_customer_approval.json
│   │   │   ├── cancelled
│   │   │   │   └── cancelled.json
│   │   │   ├── complete
│   │   │   │   └── complete.json
│   │   │   ├── draft
│   │   │   │   └── draft.json
│   │   │   ├── escalated
│   │   │   │   └── escalated.json
│   │   │   ├── flagged
│   │   │   │   └── flagged.json
│   │   │   ├── hold
│   │   │   │   └── hold.json
│   │   │   ├── in_progress
│   │   │   │   └── in_progress.json
│   │   │   ├── inspection
│   │   │   │   └── inspection.json
│   │   │   ├── new
│   │   │   │   └── new.json
│   │   │   ├── pending
│   │   │   │   └── pending.json
│   │   │   ├── qc
│   │   │   │   └── qc.json
│   │   │   ├── received
│   │   │   │   └── received.json
│   │   │   └── setup
│   │   │       └── setup.json
│   │   └── workspace
│   ├── lab
│   │   ├── api.py
│   │   ├── config
│   │   │   └── desktop.py
│   │   ├── doctype
│   │   │   ├── impedance_peak
│   │   │   │   ├── impedance_peak.json
│   │   │   │   ├── impedance_peak.py
│   │   │   │   └── __init__.py
│   │   │   ├── impedance_snapshot
│   │   │   │   ├── impedance_snapshot.json
│   │   │   │   ├── impedance_snapshot.py
│   │   │   │   └── __init__.py
│   │   │   ├── instrument_wellness_score
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instrument_wellness_score.json
│   │   │   │   └── instrument_wellness_score.py
│   │   │   ├── intonation_note
│   │   │   │   ├── __init__.py
│   │   │   │   ├── intonation_note.json
│   │   │   │   └── intonation_note.py
│   │   │   ├── intonation_session
│   │   │   │   ├── __init__.py
│   │   │   │   ├── intonation_session.json
│   │   │   │   └── intonation_session.py
│   │   │   ├── leak_reading
│   │   │   │   ├── __init__.py
│   │   │   │   ├── leak_reading.json
│   │   │   │   └── leak_reading.py
│   │   │   ├── leak_test
│   │   │   │   ├── __init__.py
│   │   │   │   ├── leak_test.json
│   │   │   │   └── leak_test.py
│   │   │   ├── measurement_entry
│   │   │   │   ├── measurement_entry.json
│   │   │   │   └── measurement_entry.py
│   │   │   ├── measurement_session
│   │   │   │   ├── measurement_session.json
│   │   │   │   └── measurement_session.py
│   │   │   ├── reed_match_result
│   │   │   │   ├── __init__.py
│   │   │   │   ├── reed_match_result.json
│   │   │   │   └── reed_match_result.py
│   │   │   ├── tone_fitness
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tone_fitness.json
│   │   │   │   └── tone_fitness.py
│   │   │   └── tone_fitness_entry
│   │   │       ├── __init__.py
│   │   │       ├── tone_fitness_entry.json
│   │   │       └── tone_fitness_entry.py
│   │   ├── __init__.py
│   │   ├── page
│   │   │   ├── impedance_recorder
│   │   │   │   ├── impedance_recorder.bundle.js
│   │   │   │   ├── impedance_recorder.html
│   │   │   │   └── impedance_recorder.py
│   │   │   ├── intonation_recorder
│   │   │   │   ├── intonation_recorder.html
│   │   │   │   └── intonation_recorder.py
│   │   │   ├── lab_dashboard
│   │   │   │   ├── lab_dashboard.bundle.js
│   │   │   │   └── lab_dashboard.json
│   │   │   ├── leak_test_recorder
│   │   │   │   ├── leak_test_recorder.bundle.js
│   │   │   │   ├── leak_test_recorder.html
│   │   │   │   └── leak_test_recorder.py
│   │   │   ├── recording_analyzer
│   │   │   │   ├── recording_analyzer.bundle.js
│   │   │   │   ├── recording_analyzer.html
│   │   │   │   ├── recording_analyzer.json
│   │   │   │   └── recording_analyzer.py
│   │   │   └── tone_fitness_recorder
│   │   │       ├── tone_fitness_recorder.bundle.js
│   │   │       ├── tone_fitness_recorder.html
│   │   │       └── tone_fitness_recorder.py
│   │   └── README.md
│   ├── logger.py
│   ├── modules.txt
│   ├── node_modules
│   ├── package.json
│   ├── patches
│   │   ├── __init__.py
│   │   ├── insert_repair_portal_workspace.py
│   │   ├── insert_workspace_placeholders.py
│   │   ├── migrate_inspection_report_to_intake_inspection.py
│   │   ├── populate_all_child_workspaces.py
│   │   ├── remove_duplicate_module_def.py
│   │   ├── remove_invalid_workspaces.py
│   │   └── v15_merge_repair_request_to_repair_order.py
│   ├── patches.txt
│   ├── player_profile
│   │   ├── doctype
│   │   │   └── player_profile
│   │   │       ├── player_profile.js
│   │   │       ├── player_profile.json
│   │   │       └── player_profile.py
│   │   ├── __init__.py
│   │   ├── notification
│   │   │   └── player_not_linked.json
│   │   ├── portal
│   │   │   └── player_profile.py
│   │   ├── README.md
│   │   ├── templates
│   │   │   └── player_profile.html
│   │   ├── workflow
│   │   │   ├── player_profile_setup
│   │   │   │   ├── *.md
│   │   │   │   └── player_profile_setup.json
│   │   │   ├── player_profile_workflow
│   │   │   │   └── player_profile_workflow.json
│   │   │   └── player_profile_workflow.json
│   │   └── workflow_state
│   │       ├── active
│   │       │   └── active.json
│   │       ├── archived
│   │       │   └── archived.json
│   │       └── linked_to_client
│   │           └── linked_to_client.json
│   ├── public
│   │   ├── css
│   │   │   ├── customer_styles.css
│   │   │   ├── instrument_history.css
│   │   │   ├── product_catalog.css
│   │   │   └── repair_request.css
│   │   ├── dist
│   │   │   ├── css
│   │   │   │   ├── adminlte.bundle.S7LYXTVT.css
│   │   │   │   ├── adminlte.bundle.S7LYXTVT.css.map
│   │   │   │   ├── adminlte.min.bundle.VYLVPENE.css
│   │   │   │   ├── adminlte.min.bundle.VYLVPENE.css.map
│   │   │   │   ├── adminlte.rtl.bundle.MXCBMNEW.css
│   │   │   │   ├── adminlte.rtl.bundle.MXCBMNEW.css.map
│   │   │   │   ├── adminlte.rtl.min.bundle.FHPADDBX.css
│   │   │   │   ├── adminlte.rtl.min.bundle.FHPADDBX.css.map
│   │   │   │   ├── profile_view.bundle.UPVOTX2B.css
│   │   │   │   └── profile_view.bundle.UPVOTX2B.css.map
│   │   │   ├── css-rtl
│   │   │   │   ├── adminlte.bundle.IE6FK2NA.css
│   │   │   │   ├── adminlte.bundle.IE6FK2NA.css.map
│   │   │   │   ├── adminlte.min.bundle.7LA3U2GM.css
│   │   │   │   ├── adminlte.min.bundle.7LA3U2GM.css.map
│   │   │   │   ├── adminlte.rtl.bundle.VTLQI4SK.css
│   │   │   │   ├── adminlte.rtl.bundle.VTLQI4SK.css.map
│   │   │   │   ├── adminlte.rtl.min.bundle.LQLA7AQM.css
│   │   │   │   ├── adminlte.rtl.min.bundle.LQLA7AQM.css.map
│   │   │   │   ├── profile_view.bundle.ORGHRCD4.css
│   │   │   │   └── profile_view.bundle.ORGHRCD4.css.map
│   │   │   ├── intake_1.bundle.3K54VPBP.js
│   │   │   ├── intake_1.bundle.3K54VPBP.js.map
│   │   │   ├── js
│   │   │   │   ├── adminlte.bundle.UGVDMH3L.js
│   │   │   │   ├── adminlte.bundle.UGVDMH3L.js.map
│   │   │   │   ├── adminlte.min.bundle.X4UZ3FZ4.js
│   │   │   │   ├── adminlte.min.bundle.X4UZ3FZ4.js.map
│   │   │   │   ├── clarinet_intake_inventory.bundle.LKA4AFHM.js
│   │   │   │   ├── clarinet_intake_inventory.bundle.LKA4AFHM.js.map
│   │   │   │   ├── clarinet_intake_repair.bundle.R6GB4P4G.js
│   │   │   │   ├── clarinet_intake_repair.bundle.R6GB4P4G.js.map
│   │   │   │   ├── client_portal.bundle.MJEUNBB2.js
│   │   │   │   ├── client_portal.bundle.MJEUNBB2.js.map
│   │   │   │   ├── customer.bundle.GWHGAP3N.js
│   │   │   │   ├── customer.bundle.GWHGAP3N.js.map
│   │   │   │   ├── impedance_recorder.bundle.2E5FFWEW.js
│   │   │   │   ├── impedance_recorder.bundle.2E5FFWEW.js.map
│   │   │   │   ├── index.bundle.DHJZZFI3.js
│   │   │   │   ├── index.bundle.DHJZZFI3.js.map
│   │   │   │   ├── intonation_recorder.bundle.ID7AGQLR.js
│   │   │   │   ├── intonation_recorder.bundle.ID7AGQLR.js.map
│   │   │   │   ├── lab_dashboard.bundle.D26WGGLG.js
│   │   │   │   ├── lab_dashboard.bundle.D26WGGLG.js.map
│   │   │   │   ├── leak_test_recorder.bundle.52BQD7UE.js
│   │   │   │   ├── leak_test_recorder.bundle.52BQD7UE.js.map
│   │   │   │   ├── recording_analyzer.bundle.XBLJC2DF.js
│   │   │   │   ├── recording_analyzer.bundle.XBLJC2DF.js.map
│   │   │   │   ├── technician_dashboard.bundle.W6PRWHBZ.js
│   │   │   │   ├── technician_dashboard.bundle.W6PRWHBZ.js.map
│   │   │   │   ├── test_1.bundle.QYWYUWA6.js
│   │   │   │   ├── test_1.bundle.QYWYUWA6.js.map
│   │   │   │   ├── test.bundle.NNZIH2J3.js
│   │   │   │   ├── test.bundle.NNZIH2J3.js.map
│   │   │   │   ├── tone_fitness_recorder.bundle.6BLF2FQ7.js
│   │   │   │   └── tone_fitness_recorder.bundle.6BLF2FQ7.js.map
│   │   │   ├── leo.bundle.EH4X7GSG.js
│   │   │   └── leo.bundle.EH4X7GSG.js.map
│   │   ├── images
│   │   │   └── svg_pad_maps
│   │   │       └── clarinet_upper_joint.svg
│   │   ├── intonation_recorder.bundle.js
│   │   ├── js
│   │   │   ├── client_portal
│   │   │   │   ├── App.vue
│   │   │   │   ├── client_portal.bundle.js
│   │   │   │   ├── customer
│   │   │   │   │   ├── customer.bundle.js
│   │   │   │   │   └── Customer.vue
│   │   │   │   ├── LayoutShell.vue
│   │   │   │   └── NotFound.vue
│   │   │   ├── intake
│   │   │   │   ├── clarinet_intake_inventory.bundle.js
│   │   │   │   └── clarinet_intake_repair.bundle.js
│   │   │   └── technician_dashboard
│   │   │       ├── App.vue
│   │   │       ├── index.bundle.js
│   │   │       └── technician_dashboard.bundle.js
│   │   ├── node_modules -> /opt/frappe/erp-bench/apps/repair_portal/node_modules
│   │   └── recording_analyzer.bundle.js
│   ├── qa
│   │   ├── config
│   │   │   └── desktop.py
│   │   ├── dashboard_chart
│   │   │   ├── average_dp_trend.json
│   │   │   ├── pass_rate_trend.json
│   │   │   ├── qa_failures_by_tech.json
│   │   │   ├── README.md
│   │   │   └── re_service_rate_trend.json
│   │   ├── data
│   │   │   └── clarinet_qc.json
│   │   ├── doctype
│   │   │   ├── final_qa_checklist
│   │   │   │   ├── final_qa_checklist.json
│   │   │   │   ├── final_qa_checklist.py
│   │   │   │   └── README.md
│   │   │   └── final_qa_checklist_item
│   │   │       ├── final_qa_checklist_item.json
│   │   │       ├── final_qa_checklist_item.py
│   │   │       └── __init__.py
│   │   ├── __init__.py
│   │   ├── notification
│   │   │   ├── critical_fail_notification.json
│   │   │   ├── followup_due_notification.json
│   │   │   ├── ncr_overdue_notification.json
│   │   │   └── README.md
│   │   ├── print_format
│   │   │   ├── __init__.py
│   │   │   ├── qc_certificate
│   │   │   │   ├── __init__.py
│   │   │   │   └── qc_certificate.json
│   │   │   ├── quality_inspection
│   │   │   │   ├── __init__.py
│   │   │   │   └── quality_inspection.json
│   │   │   └── README.md
│   │   ├── README.md
│   │   ├── report
│   │   │   ├── inspection_kpi_report
│   │   │   │   ├── __init__.py
│   │   │   │   ├── inspection_kpi_report.json
│   │   │   │   ├── inspection_kpi_report.py
│   │   │   │   └── README.md
│   │   │   └── qa_failure_rate
│   │   │       ├── qa_failure_rate.json
│   │   │       └── qa_failure_rate.py
│   │   ├── role_profile
│   │   │   ├── Client.json
│   │   │   ├── Senior_Technician.json
│   │   │   └── Technician.json
│   │   └── setup
│   │       └── __init__.py
│   ├── README.md
│   ├── repair
│   │   ├── dashboard_chart
│   │   │   ├── repair_kpis.json
│   │   │   └── repairs_by_status.json
│   │   ├── dashboard_chart_group
│   │   │   └── repair_kpis_group.json
│   │   ├── dashboard_chart_source
│   │   │   └── turnaround_time.py
│   │   ├── doctype
│   │   │   ├── default_operations
│   │   │   │   ├── default_operations.json
│   │   │   │   ├── default_operations.py
│   │   │   │   └── __init__.py
│   │   │   ├── pulse_update
│   │   │   │   ├── pulse_update.json
│   │   │   │   └── pulse_update.py
│   │   │   ├── repair_feedback
│   │   │   │   ├── repair_feedback.json
│   │   │   │   └── repair_feedback.py
│   │   │   ├── repair_issue
│   │   │   │   ├── repair_issue.json
│   │   │   │   └── repair_issue.py
│   │   │   ├── repair_note
│   │   │   │   ├── __init__.py
│   │   │   │   ├── repair_note.json
│   │   │   │   └── repair_note.py
│   │   │   ├── repair_order
│   │   │   │   ├── __init__.py
│   │   │   │   ├── README.md
│   │   │   │   ├── repair_order.js
│   │   │   │   ├── repair_order.json
│   │   │   │   └── repair_order.py
│   │   │   ├── repair_order_settings
│   │   │   │   ├── __init__.py
│   │   │   │   ├── repair_order_settings.json
│   │   │   │   └── repair_order_settings.py
│   │   │   ├── repair_request
│   │   │   │   ├── __init__.py
│   │   │   │   ├── repair_request.json
│   │   │   │   └── repair_request.py
│   │   │   └── repair_task
│   │   │       ├── __init__.py
│   │   │       ├── repair_task.json
│   │   │       └── repair_task.py
│   │   ├── email
│   │   │   └── feedback_request.html
│   │   ├── __init__.py
│   │   ├── notification
│   │   │   └── material_reorder_warning.json
│   │   ├── README.md
│   │   ├── report
│   │   │   ├── repair_issue_report
│   │   │   │   ├── repair_issue_report.json
│   │   │   │   └── repair_issue_report.py
│   │   │   ├── repair_revenue_vs_cost
│   │   │   │   ├── repair_revenue_vs_cost.json
│   │   │   │   └── repair_revenue_vs_cost.py
│   │   │   └── technician_utilization
│   │   │       ├── technician_utilization.json
│   │   │       └── technician_utilization.py
│   │   ├── scheduler.py
│   │   ├── tests
│   │   │   └── test_repair_order.py
│   │   ├── web_form
│   │   │   └── repair_request
│   │   │       └── repair_request.json
│   │   └── workspace
│   │       └── repairs.json
│   ├── repair_logging
│   │   ├── config
│   │   │   └── desktop.py
│   │   ├── custom
│   │   │   ├── customer_interaction_timeline.js
│   │   │   ├── __init__.py
│   │   │   └── item_interaction_timeline.js
│   │   ├── dashboard_chart
│   │   │   └── repair_tasks_by_day.json
│   │   ├── doctype
│   │   │   ├── barcode_scan_entry
│   │   │   │   ├── barcode_scan_entry.json
│   │   │   │   ├── barcode_scan_entry.py
│   │   │   │   └── __init__.py
│   │   │   ├── default_workflow_states
│   │   │   │   ├── default_workflow_states.json
│   │   │   │   └── default_workflow_states.py
│   │   │   ├── diagnostic_metrics
│   │   │   │   ├── diagnostic_metrics.json
│   │   │   │   ├── diagnostic_metrics.py
│   │   │   │   └── __init__.py
│   │   │   ├── environment_log
│   │   │   │   ├── environment_log.json
│   │   │   │   ├── environment_log.py
│   │   │   │   └── __init__.py
│   │   │   ├── image_log_entry
│   │   │   │   ├── image_log_entry.json
│   │   │   │   ├── image_log_entry.py
│   │   │   │   └── __init__.py
│   │   │   ├── instrument_interaction_log
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instrument_interaction_log.json
│   │   │   │   └── instrument_interaction_log.py
│   │   │   ├── instrument_photo
│   │   │   │   ├── instrument_photo.js
│   │   │   │   ├── instrument_photo.json
│   │   │   │   └── instrument_photo.py
│   │   │   ├── key_measurement
│   │   │   │   ├── __init__.py
│   │   │   │   ├── key_measurement.json
│   │   │   │   └── key_measurement.py
│   │   │   ├── material_use_log
│   │   │   │   ├── __init__.py
│   │   │   │   ├── material_use_log.json
│   │   │   │   └── material_use_log.py
│   │   │   ├── pad_condition
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pad_condition.json
│   │   │   │   └── pad_condition.py
│   │   │   ├── related_instrument_interaction
│   │   │   │   ├── __init__.py
│   │   │   │   ├── related_instrument_interaction.json
│   │   │   │   └── related_instrument_interaction.py
│   │   │   ├── repair_parts_used
│   │   │   │   ├── __init__.py
│   │   │   │   ├── repair_parts_used.json
│   │   │   │   └── repair_parts_used.py
│   │   │   ├── repair_part_used
│   │   │   ├── repair_task_log
│   │   │   │   ├── __init__.py
│   │   │   │   ├── repair_task_log.json
│   │   │   │   └── repair_task_log.py
│   │   │   ├── service_log
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service_log.json
│   │   │   │   ├── service_log.py
│   │   │   │   └── test_service_log.py
│   │   │   ├── tenon_fit_record
│   │   │   │   ├── tenon_fit_record.js
│   │   │   │   ├── tenon_fit_record.json
│   │   │   │   └── tenon_fit_record.py
│   │   │   ├── tenon_measurements
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tenon_measurements.json
│   │   │   │   └── tenon_measurements.py
│   │   │   ├── tenon_socket_measurements
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tenon_socket_measurements.json
│   │   │   │   └── tenon_socket_measurements.py
│   │   │   ├── tone_hole_inspection_record
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tone_hole_inspection_record.js
│   │   │   │   ├── tone_hole_inspection_record.json
│   │   │   │   └── tone_hole_inspection_record.py
│   │   │   ├── tool_usage_log
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tool_usage_log.json
│   │   │   │   └── tool_usage_log.py
│   │   │   ├── visual_inspection
│   │   │   │   ├── visual_inspection.json
│   │   │   │   └── visual_inspection.py
│   │   │   └── warranty_modification_log
│   │   │       ├── warranty_modification_log.json
│   │   │       └── warranty_modification_log.py
│   │   ├── __init__.py
│   │   ├── list_dashboard
│   │   │   └── instrument_tracker_dashboard.json
│   │   ├── module_def
│   │   │   └── repair_portal.json
│   │   ├── number_card
│   │   │   ├── closed_service_logs.json
│   │   │   ├── in_progress_service_logs.json
│   │   │   └── open_service_logs.json
│   │   ├── print_format
│   │   │   └── instrument_tracker_log
│   │   │       └── instrument_tracker_log.json
│   │   ├── README.md
│   │   ├── report
│   │   │   └── repair_tasks_by_type
│   │   │       ├── repair_tasks_by_type.json
│   │   │       └── repair_tasks_by_type.py
│   │   ├── workflow
│   │   │   ├── repair_task_workflow
│   │   │   │   └── repair_task_workflow.json
│   │   │   └── service_log_workflow
│   │   │       └── service_log_workflow.json
│   │   └── workflow_state
│   │       ├── closed
│   │       │   └── closed.json
│   │       ├── draft
│   │       │   └── draft.json
│   │       ├── in_progress
│   │       │   └── in_progress.json
│   │       ├── open
│   │       │   └── open.json
│   │       ├── resolved
│   │       │   └── resolved.json
│   │       └── submitted
│   │           └── submitted.json
│   ├── repair_portal
│   │   ├── config
│   │   │   └── desktop.py
│   │   ├── doctype
│   │   │   ├── consent_log_entry
│   │   │   │   ├── consent_log_entry.json
│   │   │   │   ├── consent_log_entry.py
│   │   │   │   └── __init__.py
│   │   │   ├── pulse_update
│   │   │   │   ├── __init__.py
│   │   │   │   └── pulse_update.py
│   │   │   ├── qa_checklist_item
│   │   │   │   ├── qa_checklist_item.json
│   │   │   │   └── qa_checklist_item.py
│   │   │   └── technician
│   │   │       ├── technician.js
│   │   │       ├── technician.json
│   │   │       └── technician.py
│   │   ├── __init__.py
│   │   ├── report
│   │   │   └── technician_task_summary
│   │   │       ├── technician_task_summary.json
│   │   │       └── technician_task_summary.py
│   │   └── workspace
│   ├── repair_portal.zip
│   ├── scripts
│   │   ├── buffet_import.py
│   │   ├── doctype_verify.py
│   │   ├── erpnext_clarinets_shopify.csv
│   │   ├── hooks
│   │   │   ├── clarinet_qc.py
│   │   │   ├── fix_all_workflows.py
│   │   │   ├── fix_name_key.py
│   │   │   ├── fix_workflow_states.py
│   │   │   ├── __init__.py
│   │   │   ├── insert_workflows.py
│   │   │   └── reload_all_doctypes.py
│   │   ├── __init__.py
│   │   ├── invoice_pdf
│   │   │   └── name_builder.py
│   │   ├── make_clarinetfest_ws_items.py
│   │   ├── po_import.py
│   │   ├── pre_migrate_check.py
│   │   ├── purge_shopify_items_v15.py
│   │   ├── reload_all_jsons.py
│   │   ├── shopify
│   │   ├── shopify_erpnext_clarinet_import.py
│   │   ├── shopify_to_erpnext_items.py
│   │   ├── stock_intake_utils.py
│   │   └── workflow_installer.py
│   ├── service_planning
│   │   ├── config
│   │   │   └── desktop.py
│   │   ├── dashboard_chart
│   │   │   └── scheduled_service_tasks_by_day.json
│   │   ├── doctype
│   │   │   ├── estimate_line_item
│   │   │   │   ├── estimate_line_item.json
│   │   │   │   ├── estimate_line_item.py
│   │   │   │   └── __init__.py
│   │   │   ├── repair_estimate
│   │   │   │   ├── __init__.py
│   │   │   │   ├── repair_estimate.json
│   │   │   │   └── repair_estimate.py
│   │   │   ├── service_plan
│   │   │   │   ├── service_plan.json
│   │   │   │   └── service_plan.py
│   │   │   ├── service_task
│   │   │   │   ├── service_task.json
│   │   │   │   └── service_task.py
│   │   │   └── tasks
│   │   │       ├── tasks.json
│   │   │       └── tasks.py
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── report
│   │   │   └── repair_bay_utilization
│   │   │       ├── repair_bay_utilization.json
│   │   │       └── repair_bay_utilization.py
│   │   ├── workflow
│   │   │   └── service_task_workflow.json
│   │   └── workflow_state
│   │       ├── completed.json
│   │       ├── in_progress.json
│   │       └── scheduled.json
│   ├── setup
│   │   └── patches
│   │       └── utils
│   │           └── user_utilities.py
│   ├── stock
│   │   └── doctype
│   │       ├── delivery_note
│   │       │   └── delivery_note.py
│   │       └── stock_entry
│   │           └── stock_entry.py
│   ├── templates
│   │   ├── clarinet_initial_setup_certificate.html
│   │   ├── generators
│   │   │   └── instrument_profile.html
│   │   ├── __init__.py
│   │   ├── pages
│   │   │   ├── clarinetfest-2025.html
│   │   │   ├── customer.html
│   │   │   ├── __init__.py
│   │   │   ├── instrument_wellness.html
│   │   │   ├── my_instruments.html
│   │   │   ├── my_players.html
│   │   │   ├── my_repairs.html
│   │   │   ├── pad_map.html
│   │   │   ├── player_profiles.html
│   │   │   ├── repair_pulse.html
│   │   │   ├── repair_request.html
│   │   │   └── repair_status.html
│   │   └── recording_analyzer.html
│   ├── __test__.py
│   ├── tests
│   │   ├── test_api.py
│   │   └── test_clarinet_intake.py
│   ├── tools
│   │   ├── config
│   │   │   └── desktop.py
│   │   ├── dashboard_chart
│   │   │   └── overdue_tools_by_type.json
│   │   ├── doctype
│   │   │   ├── tool
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tool.json
│   │   │   │   └── tool.py
│   │   │   └── tool_calibration_log
│   │   │       ├── tool_calibration_log.json
│   │   │       └── tool_calibration_log.py
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── report
│   │   │   └── overdue_tool_calibrations
│   │   │       ├── overdue_tool_calibrations.json
│   │   │       └── overdue_tool_calibrations.py
│   │   ├── stock_tools.py
│   │   ├── workflow
│   │   │   └── tool_lifecycle
│   │   │       └── tool_lifecycle.json
│   │   ├── workflow_state
│   │   │   ├── available
│   │   │   │   └── available.json
│   │   │   ├── out_for_calibration
│   │   │   │   └── out_for_calibration.json
│   │   │   └── retired
│   │   │       └── retired.json
│   │   └── workspace
│   │       └── tools
│   │           └── tools.json
│   ├── trade_shows
│   │   └── __init__.py
│   ├── validation_log.txt
│   ├── www
│   │   ├── clarinetfest-2025-catalog.html
│   │   ├── client_portal
│   │   │   ├── App.vue
│   │   │   └── client_portal.bundle.js
│   │   ├── instrument_profile.html
│   │   ├── instrument_profile.py
│   │   ├── instrument_wellness.py
│   │   ├── my_instruments.py
│   │   ├── my_players.py
│   │   ├── my_repairs.py
│   │   ├── pad_map.py
│   │   ├── player_profiles.py
│   │   ├── portal
│   │   │   ├── my_customer.html
│   │   │   ├── my_customer.py
│   │   │   ├── player_profile.html
│   │   │   └── player_profile.py
│   │   ├── README.py
│   │   ├── repair_pulse.py
│   │   ├── repair_request.py
│   │   ├── repair_status.py
│   │   ├── service_summary.py
│   │   └── trial.py
│   └── yarn.lock
├── ruff.toml
├── setup.py
├── validate_app.py
└── yarn.lock

367 directories, 747 files
```

*Always use absolute paths.* Never guess; verify against the repo.

---

## 3 · File‑Block Contribution Rules

````text
1. One file per fenced block:
   ```python name=path/to/file.py```
2. Show **full relative paths**.
3. Provide complete, runnable code—no `TODO`, no ellipses.
4. Finish with the **Verification Checklist** (see §10).
````

---

## 4 · Coding Standards

| Layer             | Must‑Use Patterns                                                |
| ----------------- | ---------------------------------------------------------------- |
| **Python**        | PEP 8 • Typed hints • `frappe.get_doc` • File header template    |
| **JavaScript**    | `frappe.ui.form.on` • No inline HTML • ARIA labels for portal    |
| **JSON DocTypes** | "engine": "InnoDB" • `workflow_state_field` present              |
| **HTML Files**    | Use Jinja templating in html files when necessary                |
| **.VUE Files      | Use .vue files in the public/js/* directory as much as possible  |
| **Comments**      | English first; add Spanish if the ticket is in Spanish (EN + ES) |

### Python File Header

```python
# Relative Path: repair_portal/<module>/...
# Last Updated: YYYY‑MM‑DD
# Version: vX.X
# Purpose: ...
# Dependencies: ...
```

---

## 5 · Compliance Checklist (Frappe v15)

* `workflow_state` **Select**, never Link
* Zero deprecated keys (`__onload`, etc.)
* Tests pass via `bench --site erp.artisanclarinets.com run-tests`
* No orphaned DocTypes, fields, or circular imports

---

## 6 · Domain‑Specific Automations

| Trigger                         | Automation                                                                      |
| ------------------------------- | ------------------------------------------------------------------------------- |
| `Clarinet Intake` **Inventory** | Create **Serial No**, **Initial Intake Inspection**, **Clarinet Initial Setup** |
| JS & PY Controllers             | Use controllers for conditional fields & all automations                        |
| Technician Portal               | Must be keyboard‑navigable; include ARIA labels                                 |

---

## 7 · Quality Gates

1. Lint Python & JSON.
2. Validate DocTypes with `frappe.get_meta`.
3. Generate or update tests under `/tests/`.
4. Log exceptions using `frappe.log_error()`.

---

## 8 · Security & Governance

* No credentials or PII in code or logs.
* Honor Frappe permission model; default‑deny mindset.
* Delete files **only** after explicit approval and backup confirmation.

---

## 9 · Continuous Improvement

* Maintain `/opt/frappe/erp-bench/apps/repair_portal/CHANGELOG.md`.
* Review technical debt quarterly; propose refactors.
* Optimize server‑side queries and API calls; target <200 ms.

---

## 10 · Verification Checklist

```bash
# Pull latest and migrate
bench --site erp.artisanclarinets.com migrate

# Build assets
bench build

# Run targeted tests
bench --site erp.artisanclarinets.com run-tests --module repair_portal.tests.intake
```

---

### Need Help?

Ping Dylan Thompson and ask any questions needed. The clarinets—and the concerts—are counting on you. 🎶
