# Instrument Profile Module

Manages a clarinet’s full lifecycle: history, valuation, upgrades, and legal ownership.

## Features Implemented
- ✅ Lifetime Timeline
  - Scrollable feed of **Instrument Events** and player comments
  - Aggregates Repair Orders, photos, and manual notes
- ✅ "Next Upgrade" suggestions with route to `/repair-hub/upgrade`
- ✅ Market-Value Tracker
  - Scheduled script pulls average valuations from eBay/Reverb
  - Field stored on Instrument
- ✅ Upgrade Wishlist
  - Table field: upgrade parts with link to shop/quote
- ✅ Ownership Transfer
  - Verification steps for handoff
  - PII from old owner removed
- ✅ Insurance Report Generator
  - Public PDF with instrument stats, images, history

## Developer Notes
- All fields on `Instrument` doctype or child tables
- Scheduler jobs in `instrument_profile.scheduler`

---
Last updated: 2025-07-12