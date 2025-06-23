# Repair Module – MRW Artisan Instruments

**Last Updated:** 2025-06-15  
**Version:** 1.0  
**Maintainer:** Dylan Thompson / MRW Artisan Instruments

---

## 📌 Purpose
Central control module for all clarinet repair workflow stages:
- Intake → Inspection → Service Planning → Repair Execution → QA → Delivery
- Tracks tasks, time, SLA, part usage, technician performance, and customer feedback

---

## 📁 Contents

### DocTypes
- `Repair Order`: Core job record
- `Repair Task`: Child task rows
- `Repair Order Settings`: SLA defaults and technician config
- `Repair Feedback`: Linked to Repair Order from portal

### Workflow
- `repair_order_workflow.json`: Status automation from Draft to Closed

### UI
- Customer portal: `/www/repair_status.html`
- Workspace: `repair/workspace/repairs.json`
- Dashboard: `repair/dashboard_chart/repair_kpis.json`

### Scripts
- `scheduler.py`: Daily SLA checker, triggers alerts
- `repair_order.py`: Core logic – totals, delays, instrument linkage
- `repair_feedback.py`: Validation for customer feedback entries

---

## 🚀 Features
- SLA alerting + visual flagging
- Feedback email and portal integration
- Instrument Profile auto-updated with every repair
- KPI dashboard widgets for managers
- Fully extensible and linked across all modules

---

## 🧪 Testing
- Covered in `test_repair_order.py`
- Includes full lifecycle: create, plan, execute, QA, feedback

---

## 🔗 Integration
- Ties to: `Clarinet Intake`, `Service Plan`, `Instrument Profile`, `Material Usage`, `Setup Log`
- Fully portal-ready for high-end customer transparency

---

## 🔧 To Extend Next
- Technician auto-routing
- Automated invoicing + GL integration
- Repeat repair tracking / warranty flags