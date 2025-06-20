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
├── PLANNED_FEATURES.md
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

---

## 🔮 Planned Features
See [PLANNED_FEATURES.md](./PLANNED_FEATURES.md) for:
- Background Tuner Overlay
- Chromatic Drone Generator
- Spring-Force Calculator
- Cork Thickness Finder
- Bore-Profile Scanner

## 🚦 Status
Production-ready ✅

*File last updated: 2025-06-19 / v1.1*