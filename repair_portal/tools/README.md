# Tools Module

## 🎯 Purpose
Track specialized and general tools, manage calibration schedules, and monitor lifecycle status of all instruments used in clarinet repair operations.

## 📂 Structure
```
tools/
├── doctype/
│   ├── tool/
│   └── tool_calibration_log/
├── report/
│   └── overdue_tool_calibrations/
├── dashboard_chart/
│   └── overdue_tools_by_type.json
├── workflow/
│   └── tool_lifecycle.json
├── workspace/
│   └── repair_tools_&_utilities.json
├── config/
│   └── desktop.py
└── README.md
```

## ✅ Doctypes
- Tool
- Tool Calibration Log

## 📊 Reports
- Overdue Tool Calibrations ✅

## 📈 Dashboard Charts
- Overdue Tools by Type ✅

## 🔁 Workflows
- Tool Lifecycle ✅
  - States: Available → Out for Calibration → Retired

## 🔒 Permissions
- `Technician` (Read), `Service Manager`, `System Manager`

## 🚦 Status
Production-ready ✅