# Service Planning Module

## 🎯 Purpose
Schedule and manage planned service tasks across repair bays and technician workloads.

## 📂 Structure
```
service_planning/
├── doctype/
│   ├── service_plan/
│   └── service_task/
├── report/
│   └── repair_bay_utilization/
├── dashboard_chart/
│   └── scheduled_service_tasks_by_day.json
├── workflow/
│   └── service_task_workflow.json
├── workspace/
│   └── service_planning.json
├── config/
│   └── desktop.py
└── README.md
```

## ✅ Doctypes
- Service Plan
- Service Task (includes scheduling, technician, repair bay)

## 📊 Reports
- Repair Bay Utilization ✅

## 📈 Dashboard Charts
- Scheduled Service Tasks by Day ✅

## 🔁 Workflows
- Service Task Workflow ✅
  - States: Scheduled → In Progress → Completed

## 🔒 Permissions
- `Technician`, `Service Manager`

## 🚦 Status
Production-ready ✅