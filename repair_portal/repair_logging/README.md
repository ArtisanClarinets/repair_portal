# Repair Logging Module

## 🛠️ Purpose
Logs and audits all technician activities, tool usage, and instrument progress throughout the repair lifecycle.

## 📁 Structure
```
repair_logging/
├── config/desktop.py
├── doctype/
│   ├── instrument_interaction_log/
│   ├── instrument_tracker/
│   ├── related_instrument_interaction/
│   ├── repair_task_log/
│   └── tool_usage_log/
├── print_format/
│   └── instrument_tracker_log/
├── report/
│   └── custom_doctype_report/
├── custom/
│   ├── customer_interaction_timeline.js
│   └── item_interaction_timeline.js
├── workspace/
│   └── repair_logging/
│       └── repair_logging.json
└── README.md (you are here)
```

## 🧾 Doctypes
- **Instrument Tracker**: Central node tracking full job lifecycle.
- **Repair Task Log**: Performed repairs and task assignments.
- **Tool Usage Log**: Timestamped usage of technician tools.
- **Instrument Interaction Log**: Detail-level technician interactions.
- **Related Instrument Interaction**: Relational doctype for context.

## 📊 Reports
- **Custom Doctype Report**: Sample or dynamic report templates.

## 🖨️ Print Formats
- Instrument Tracker Log

## 🧩 Links
- Ties directly into Intake workflow via Clarinet Intake reference.
- Feeds forward into QA/Enhancement assessment.
- JS injectors extend Customer and Item views.

## 📎 Status
✅ Production Ready