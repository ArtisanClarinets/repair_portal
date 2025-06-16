# Inspection Module

## 🧪 Purpose
Manage pre-service inspection of instruments, standardize checklists, and triage to setup or repair.

## 📂 Structure
```
inspection/
├── doctype/
│   ├── clarinet_condition_assessment/
│   ├── inspection_template/
│   ├── inspection_checklist_section/
│   └── inspection_checklist_item/
├── report/
│   ├── inspection_failure_rates/
│   └── top_failing_categories/
├── workspace/inspection/
└── README.md
```

## ✅ Core Features
- Inspection templating for reusable workflows
- Pass/fail logic for every checklist item
- Automatic routing to setup or repair
- Linkage to Instrument Tracker on submit

## 📊 Reports
- **Inspection Failure Rates**: by technician
- **Top Failing Categories**: most common failing items

## ⚙️ Automation
- Template populates child table sections/items
- On Submit → creates Initial Setup or Repair Log based on condition

## 🔗 Integrations
- Links to `Clarinet Model`, `Instrument Tracker`, `Customer`
- Passes control to downstream flows

## 🚦 Status
Production-ready with analytics, templating, and submission logic