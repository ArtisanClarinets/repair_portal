# Intake Module

## 📦 Purpose
Manages customer instrument intake for clarinet repairs. Tracks payment, loaners, checklists, communication, and document logs.

## 📁 Structure
```
intake/
├── config/desktop.py
├── doctype/
│   ├── clarinet_intake/
│   ├── customer_consent_form/
│   ├── customer_upgrade_request/
│   └── intake_checklist_item/
├── dashboard_chart/
│   ├── avg_intake_to_repair_time.json
│   ├── intakes_due_soon.json
│   └── overdue_intakes.json
├── print_format/
│   └── intake_receipt.json
├── report/
│   ├── deposit_balance_aging/
│   ├── loaner_turnover/
│   ├── followup_compliance/
│   └── intake_by_day/
├── workspace/
│   └── repair_portal/
│       └── repair_portal.json
├── workflow/
│   └── clarinet_intake_workflow.json
└── README.md (you are here)
```

## 📎 Doctypes Summary
| Doctype                  | Description                                      | Python Controller                                      |
|--------------------------|--------------------------------------------------|--------------------------------------------------------|
| Clarinet Intake          | Primary intake form for clarinet service        | `clarinet_intake.py`                                   |
| Customer Consent Form    | Linked consent documents                        | `customer_consent_form.py`                             |
| Customer Upgrade Request | Customer-requested service upgrades             | `customer_upgrade_request.py`                          |
| Intake Checklist Item    | Line items/checks for instrument intake review  | `intake_checklist_item.py`                             |

## 🧠 Key Functions (Clarinet Intake)
| Function      | Purpose                                                           |
|---------------|-------------------------------------------------------------------|
| `on_submit()` | Create/update Instrument Tracker, append intake interaction log  |

## 🧩 Linked Systems
- `Instrument Tracker` (via serial number link)
- `Repair Logging` for chronological interactions

## 🔧 Status
✅ Fully integrated and deployed

## 🔍 Notes
- Intake Receipt print format uses `instrument_description`, which should be calculated.
- Consider extending workspace with shortcuts, charts, and quick lists.