# AGENTS.md — repair_logging Module

## 🔍 Purpose
Handles all repair-related documentation:
- Step-by-step repair logs
- Technician uploads
- Pad map drawings and annotations

## 📁 Structure
- `doctype/repair_status_update/` — child table for live repair updates
- `doctype/pad_map/` — schematics and visual logs
- `report/` — technician-specific insights and checklists

## ✅ Validation
- Must include `repair_request` link if nested
- Always call `frappe.publish_realtime()` for live updates from server

## 🎯 Contribution
- All updates must flow through parent DocType: `Repair Request`
- Add Vue3 components for live front-end updates
- Secure all writes to Technician role only

## 🧠 Agent Notes
- Keep `status_update` records timestamped accurately
- If `status = Complete`, emit a realtime update event
- Cross-reference `Repair Step` against `Repair Plan` in future integrations
