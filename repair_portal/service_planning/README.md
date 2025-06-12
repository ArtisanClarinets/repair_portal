# Service Planning Module

## 🗓️ Purpose
Organizes upcoming repairs into structured, date-based service plans. Coordinates technician workload using diagnostic inputs and scheduling tools.

## 📁 Structure
```
service_planning/
├── config/desktop.py
├── doctype/
│   ├── service_plan/
│   └── service_task/
├── workspace/service_planning/
│   └── service_planning.json
└── README.md (you are here)
```

## 📋 Doctypes
- **Service Plan**: Root planning entity, linked to Instrument and Tasks
- **Service Task**: Atomic repair task (bench-level) with schedule + technician

## 🔗 Workflow
- Input from Inspection findings
- Breaks into tasks → Assigns to available technicians
- Tracked via Instrument Tracker & Logging

## 📎 Status
✅ Fully linked with Logging, QA, and Enhancements modules