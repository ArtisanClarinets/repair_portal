# Client-Facing Repair Portal

This module powers the user-facing interface where clients interact with their repair jobs.

## Features Implemented
- ✅ Unified Chat & Ticketing
  - Threaded messages per job
  - Email + SMS + Web channel integration
  - Admin settings at `Repair Portal Settings`
- ✅ Job Progress Thermometer
  - Tracks workflow from intake to shipping
  - Client portal component at `/repair_progress?name=REQ-####`
- ❌ Financing & Split Payments *(Deferred)*
- ✅ Referral Rewards
  - Clients receive/share referral links with automatic coupon generation
- ✅ PWA + Push Notifications
  - Service worker enabled; push via status update hooks

## Admin Access
- All features configured via `Repair Portal Settings` (singleton)

## Portal Views
- `/repair_progress`
- `/customer_sign_off`
- `/referral`
- `/chat`

## Development Notes
- SMS via Twilio with backend config in `repair_portal_settings`
- Websocket & polling integration under `www/chat/index.html`

---
Last updated: 2025-07-03