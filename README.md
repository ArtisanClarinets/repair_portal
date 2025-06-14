# Repair Portal for Artisan Clarinets

## 🎯 Overview
This Frappe-based ERPNext app is a comprehensive clarinet repair and tracking system. It supports intake, inspection, service planning, repair, QA, enhancements, and interaction logging across instruments, customers, and items.

---

## 📦 Modules & Features

### 1. Intake
- Clarinet Intake, Approvals, SLAs, and Communications

### 2. Instrument Profile ✅ (Newly Rebuilt)
- Tracks customer & shop-owned instruments
- Links to Condition Logs, Setup History
- Web Form for customer self-registration
- Public Page: Instrument History
- Dashboard + Chart + Workflow + Validation Logic

### 3. Repair Logging
- Instrument Tracker from Intake through QA
- Aging reports, compliance charts

### 4. QA, Inspection, Enhancements
- Final QA, Inspection templates, Upgrade Requests

### 5. Service Planning & Tools
- Part planning, timeline views, cross-linked logs

---

## 🧩 Developer Map
```
repair_portal/
├── enhancements/
├── inspection/
├── instrument_setup/
├── intake/
├── instrument_profile/        ◀️ rebuilt
├── qa/
├── repair_logging/
├── service_planning/
├── tools/
└── repair_portal/
```

---

## 📊 Reports & Dashboards
- Intake Reports, Repair KPIs
- Instrument Inventory & Status Distribution

## 🌐 Website Pages
- `/instrument-history/<serial>`
- `/instrument-registration` (Web Form)

## 🛠️ Bench Setup
```bash
cd /opt/frappe/erpnext-bench
source /opt/frappe/venv/bin/activate
bench --site erp.artisanclarinets.com migrate
bench --site erp.artisanclarinets.com clear-cache
```

## ✅ Status
**Fully Production Ready** (as of 2025-06-14)