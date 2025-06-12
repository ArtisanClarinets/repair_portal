# Repair Portal for Artisan Clarinets

## 🎯 Overview
This Frappe-based ERPNext app is a comprehensive clarinet repair and tracking system. It supports intake, inspection, service planning, repair, QA, enhancements, and interaction logging across instruments, customers, and items.

---

## 📦 Modules & Features

### 1. Intake
- **Clarinet Intake** and support Doctypes:
  - Intake Followup
  - Intake SLA
  - Intake Photo
  - Intake Comm Log
  - Intake Document
  - Clarinet Intake Payment
  - Clarinet Loaner Instrument
  - Intake Approval
- Print format: Intake Receipt
- Workflow: Clarinet Intake Workflow
- Workspace: Intake Workspace

### 2. Repair Logging
- **Instrument Tracker** system
  - Tracks from Intake through QA
  - Reports:
    - Deposit Balance Aging
    - Loaner Turnover
    - Intake by Day
    - Followup Compliance
  - Charts:
    - Overdue Intakes
    - Intakes Due Soon
    - Avg Intake-to-Repair Time

### 3. QA, Inspection, Enhancements
- QA: Final QA Checklist
- Inspection: Condition Assessment
- Enhancements: Customer Upgrade Request

### 4. Service Planning
- Includes: Service Plan, Parts Needed, Approval Records

### 5. Setup, Tools, Custom Scripts
- Instrument Models, Parts Setup
- Timeline-enhanced customer & item interaction logs
- Field injection via JSON fixtures

---

## 🧩 Developer Map (Updated)
```
repair_portal/
├── enhancements/
├── inspection/
├── instrument_setup/
├── intake/
│   ├── doctype/
│   ├── dashboard_chart/
│   ├── report/
│   ├── print_format/
│   └── workspace/
├── qa/
├── repair_logging/
│   ├── doctype/
│   ├── report/
│   └── print_format/
├── service_planning/
├── tools/
├── repair_portal/
│   ├── config/
│   ├── workflow/
│   └── workspace/
└── README.md (you are here)
```

---

## 📊 Reports & Dashboards
- Loaner Turnover
- Intake by Day
- Followup Compliance
- Deposit Balance Aging
- Dashboard Charts:
  - Avg Intake to Repair Time
  - Overdue Intakes
  - Intakes Due Soon

---

## 🛠️ Bench Setup
```bash
cd /opt/frappe/erpnext-bench
source /opt/frappe/venv/bin/activate
bench --site erp.artisanclarinets.com migrate
bench --site erp.artisanclarinets.com clear-cache
```

## 🧪 Testing Checklist
- [x] Intake triggers Instrument Tracker
- [x] Tracker logs events from each phase
- [x] Dashboard charts populate correctly
- [x] Reports display without error
- [x] Print formats render properly

---

## 📎 Status
✅ **Production Ready & Actively Maintained**