# Repair Portal for Artisan Clarinets

## 🎯 Overview
This Frappe-based ERPNext app is a comprehensive clarinet repair and tracking system. It supports intake, inspection, service planning, repair, QA, and enhancements with timeline views across instruments, customers, and item models.

---

## 📦 Modules & Features

### 1. Intake
- **Clarinet Intake**: Logs instrument details (serial, item, customer).
- Auto-logs to: Instrument Tracker

### 2. Repair Logging
- **Instrument Tracker**: Central record per instrument
  - Links to `Clarinet Intake`
  - Contains a `interaction_logs` child table
  - Client-side timeline UI
  - CSV export + print format
- Auto-populated from:
  - Clarinet Intake
  - Condition Assessment
  - Service Plan
  - Repair Task Log
  - Final QA Checklist
  - Upgrade Request

### 3. Customer Interaction Log
- Adds `related_interactions` table to Customer
- Populated by `Instrument Tracker` `on_update`
- Timeline and filters included

### 4. Item Interaction Log
- Adds `related_interactions` table to Item
- Populated by `Instrument Tracker` `on_update`
- Timeline and filters included

---

## 🧩 Developer Map

```
repair_portal/
├── instrument_setup/
│   └── clarinet_intake/
├── inspection/
│   └── clarinet_condition_assessment/
├── service_planning/
│   └── service_plan/
├── repair_logging/
│   ├── instrument_tracker/
│   ├── instrument_interaction_log/
│   ├── related_instrument_interaction/
│   ├── repair_task_log/
│   └── print_format/instrument_tracker_log/
├── qa/
│   └── final_qa_checklist/
├── enhancements/
│   └── customer_upgrade_request/
└── custom/
    ├── customer_interaction_log_field.json
    ├── customer_interaction_timeline.js
    └── item_interaction_timeline.js
```

---

## 🛠️ Bench Setup
```bash
cd /opt/frappe/erpnext-bench
source /opt/frappe/venv/bin/activate
bench --site erp.artisanclarinets.com migrate
bench --site erp.artisanclarinets.com clear-cache
```

## 🧪 Testing Checklist
- [x] Submit Clarinet Intake → new Instrument Tracker created
- [x] Submit Inspection → log appended
- [x] Submit Repair Task → log appended
- [x] View timeline on Instrument, Customer, Item
- [x] Export CSV
- [x] Print Format works

---

## 📎 Status
✅ **Production Ready**