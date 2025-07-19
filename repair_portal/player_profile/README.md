# Player Profile Module

**Location:** `repair_portal/player_profile/`

## Overview
Player Profile manages musician identity, permissions, compliance, and analytics for students and clients. It is fully portal-ready, compliant with data privacy (COPPA/FERPA), and integrates all session, service, and audit history. Designed for ERPNext v15.

---

## Main Features

- **ERPNext Integration:**
  - Each profile links to Customer and Instrument Profiles for master data hygiene.
  - All logs—setup, QA, repairs, intonation, wellness—are tracked as child tables for 360° audit.
- **Workflow & UX:**
  - Workflow-driven status (Draft, Active, Archived), with dashboard headline and context-aware buttons (Activate, Archive, Restore).
  - No inline HTML, all UI logic via Frappe API. All buttons and labels localized for global use.
  - Portal analytics: exposes session/repair/QA stats and compliance via `/portal/player_profile.py`.
- **Compliance:**
  - Age-based marketing block with parental notification (COPPA safe).
  - Portal route and page protection—parents and profile owners only.
- **Navigation:**
  - `links` array in doctype for instant nav to Customer, Instrument Profile.
- **Notifications:**
  - Parental email is sent if compliance triggers a marketing block.
- **Portal Analytics:**
  - Full context, session history, compliance flags, and repair/QA analytics in portal context.

---

## Portal API: `/portal/player_profile.py`
- Returns full player context, linked logs, session analytics, compliance status, and parent email if blocked.
- Validates user permissions and protects all PII.

---

## Change Log (see root CHANGELOG.md for details)
- 2025-07-17: Portal script, Restore button, compliance notifications, nav links, and dashboard enhancements added.
- 2025-06-30: Notes field refactor for technician/internal UX.
