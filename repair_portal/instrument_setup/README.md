# Instrument Setup Module

## 🧰 Purpose
Defines setup steps, inspection checklists, technician assignments, material tracking, and quality validation for new or overhauled clarinets.

## 📁 Structure
```
instrument_setup/
├── config/desktop.py
├── dashboard/repairs_dashboard.json
├── dashboard_chart/
│   ├── repairs_by_status.json
│   └── common_inspection_findings.json
├── doctype/
│   ├── clarinet_initial_setup/ (with auto-assignment, stock check, material request logic)
│   ├── clarinet_inspection/
│   ├── clarinet_setup_log/
│   ├── clarinet_setup_operation/
│   ├── inspection_finding/
│   ├── material_usage/
│   ├── setup_checklist_item/
│   └── setup_template/
├── report/
│   ├── turnaround_time_analysis/
│   ├── technician_performance/
│   └── parts_consumption/
├── test/
│   ├── test_clarinet_initial_setup.py
│   └── test_automation_and_kpi.py
├── web_form/repair_status/
├── workspace/instrument_setup.json
└── README.md (you are here)
```

## 📊 KPIs & Dashboards
- **Dashboard Charts**:
  - Repairs by Status
  - Common Inspection Findings
- **Metrics & Automation**:
  - Technician Error Rate
  - Checklist Completion Rate
  - Setup Time per Model

## ⚙️ Automations
- Auto-assigns available technician
- Validates stock levels from `Bin`
- Auto-creates `Material Request` upon submit
- Notifies if stock insufficient

## 🧪 Testing Coverage
- Technician assignment logic
- Checklist KPI count
- Material flow simulation via `test_automation_and_kpi.py`

## 🌐 Client-Side Enhancements
- Color-coded statuses
- Custom dashboard messages
- Setup timer button on UI

## ✅ Status
Fully production-ready, validated, tested, integrated with Inventory, enhanced for technician workflows and automation.