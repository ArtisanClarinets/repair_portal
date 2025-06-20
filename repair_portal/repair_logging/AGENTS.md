# AGENTS.md — repair_logging Module

## 🔍 Purpose
Handles all repair-related documentation and live agent integrations for the Repair Portal.
- Step-by-step repair logs
- Technician uploads
- Pad map drawings and annotations
- Support for ChatGPT/Codex model integration (AGENTS)

## 📁 Structure
- `doctype/repair_status_update/` — child table for live repair updates
- `doctype/pad_map/` — schematics and visual logs
- `report/` — technician-specific insights and checklists

## ✅ Validation
- Must include `repair_request` link if nested
- Always call `frappe.publish_realtime()` for live updates from server
- Ensure all agent-driven entries have a clear user/agent ID, timestamp, and edit log

## 🤖 ChatGPT/Codex Agent Integration
- All real-time suggestions, repair checklists, or AI-guided flows are logged with `source: agent` and agent version
- Agent can:
  - Draft repair steps based on current state
  - Suggest parts or pads based on pad map + instrument model
  - Validate technician input (auto-check for missing photos, critical steps)
  - Auto-prompt for before/after photos
  - Escalate complex issues to human supervisor
- Ensure AGENTS are limited to suggestion unless Technician grants write/approve
- Log agent actions for audit and improvement

## 🎯 Contribution
- All updates must flow through parent DocType: `Repair Request`
- Add Vue3 components for live front-end updates
- Secure all writes to Technician role only

## 🧠 Agent Notes
- Keep `status_update` records timestamped accurately
- If `status = Complete`, emit a realtime update event
- Cross-reference `Repair Step` against `Repair Plan` in future integrations
- Maintain compatibility with future model (e.g. GPT-5/Code Interpreter upgrades)

---

*Last updated: 2025-06-19 / v2.0*