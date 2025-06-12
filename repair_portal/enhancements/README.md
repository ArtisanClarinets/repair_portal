# Enhancements Module

## ✨ Purpose
Track and fulfill customer-authorized upgrades to instruments, such as plating, accessories, or cosmetic repairs.

## 📁 Structure
```
enhancements/
├── config/desktop.py
├── doctype/
│   ├── customer_upgrade_request/
│   └── upgrade_option/
└── README.md (you are here)
```

## 📋 Doctypes
- **Customer Upgrade Request**: Logs each enhancement interest and tracks approval status.
- **Upgrade Option**: Predefined service add-ons selectable within requests.

## 🔁 Flow
- Triggered post-intake
- Can be initiated by customer or suggested by technician
- Routed through Manager approval
- Tracked via Instrument Tracker

## 📎 Status
✅ Fully implemented and linkable to Instrument Tracker
