# Repair Logging Module

## 🎯 Purpose
Log all repair actions, parts used, interactions, and tool usage during clarinet repair operations. Enables QA visibility and tracking by technician and task type.

## 📂 Structure
```
repair_logging/
├── doctype/
│   ├── repair_task_log/
│   ├── tool_usage_log/
│   ├── instrument_tracker/
│   ├── instrument_interaction_log/
│   └── related_instrument_interaction/
├── report/
│   └── repair_tasks_by_type/
├── dashboard_chart/
│   └── repair_tasks_by_day.json
├── workflow/
│   └── repair_task_workflow.json
├── print_format/
│   └── instrument_tracker_log.json
├── custom_script/
│   └── customer_and_item_interactions.json
└── README.md
```

## ✅ Doctypes
- Repair Task Log
- Tool Usage Log
- Instrument Tracker
- Instrument Interaction Log
- Related Instrument Interaction

## 📊 Reports
- Repair Tasks by Type ✅

## 📈 Dashboard Charts
- Repair Tasks by Day ✅

## 🔁 Workflows
- Repair Task Workflow ✅
  - Draft → In Progress → Submitted

## 📝 Print Formats
- Instrument Tracker Log ✅

## 🔒 Permissions
- `Technician`, `QA`, `Service Manager`

## 🚦 Status
Production-ready ✅