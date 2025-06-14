# Intake Module

## 🎯 Purpose
Expanded to support customer appointments, loaner management, return inspection, and intake scheduling.

## 📂 Structure
```
intake/
├── doctype/
│   ├── appointment/
│   ├── clarinet_intake/
│   ├── customer_consent_form/
│   ├── intake_checklist_item/
│   ├── loaner_instrument/
│   └── loaner_return_check/
├── report/
│   ├── intake_by_day/
│   ├── loaner_turnover/
│   ├── follow_up_compliance/
│   ├── upcoming_appointments/
│   ├── loaners_outstanding/
│   └── loaner_return_flags/
├── dashboard_chart/
│   ├── overdue_intakes.json
│   ├── intakes_due_soon.json
│   ├── avg_intake_to_repair_time.json
│   ├── appointments_by_week.json
│   └── loaners_checked_out.json
├── workflow/
│   ├── clarinet_intake_workflow.json
│   ├── appointment_workflow.json
│   └── loaner_return_check_workflow.json
├── print_format/
│   └── intake_receipt.json
├── web_form/
│   └── clarinet_intake_request/
└── README.md
```

## ✅ Expanded Doctypes
- Clarinet Intake
- Customer Consent Form
- Intake Checklist Item (child)
- Appointment ✅ (with workflow)
- Loaner Instrument ✅
- Loaner Return Check ✅ (with workflow)

## 📊 Reports
- Intake By Day
- Loaner Turnover
- Follow-Up Compliance
- **Upcoming Appointments** ✅
- **Loaners Outstanding** ✅
- **Loaner Return Flags** ✅

## 📈 Dashboards
- Overdue Intakes
- Intakes Due Soon
- Avg Intake-to-Repair Time
- **Appointments by Week** ✅
- **Loaners Checked Out** ✅

## 🔁 Workflow
- Clarinet Intake Workflow
- Appointment Workflow ✅
- Loaner Return Check Workflow ✅

## 🚦 Status
Production-ready ✅