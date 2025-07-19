# Tools Module

## 🎯 Purpose
Track specialized and general tools, manage calibration schedules, monitor lifecycle status, and ensure full financial/audit traceability via ERPNext Asset integration.

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
  - Now links to ERPNext Asset for financial tracking (`asset` field)
  - Calibration notifications automated (see Automation)
- Tool Calibration Log

## 📊 Reports
- Overdue Tool Calibrations ✅

## 📈 Dashboard Charts
- Overdue Tools by Type ✅

## 🔁 Workflows
- Tool Lifecycle ✅
  - States: Available → Out for Calibration → Retired
  - State managed by workflow automation and read-only field

## 🔒 Permissions
- `Technician` (Read), `Service Manager`, `System Manager`

## 🤖 Automation
- **Calibration Due Notifications:**
  - Nightly, all tools requiring calibration within 7 days trigger a notification to owner (and can be extended to managers)
  - Robust error logging for audit
- **ERPNext Asset Integration:**
  - New field (`asset`) for linking or creating Asset in ERPNext for depreciation, insurance, or accounting needs

## 🚦 Status
Production-ready ✅

## 🗂️ Change Log
- 2025-07-17: Calibration due notification and ERPNext Asset link field added. Audit logging and README updated.
