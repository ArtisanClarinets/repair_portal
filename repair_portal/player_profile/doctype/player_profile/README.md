# Player Profile Doctype Overview

## Files Reviewed
- player_profile.js
- player_profile.py

## Purpose
Persistent CRM profile for musicians/players, handling identity, preferences, marketing, compliance, and actionable CRM triggers.

## Main Functions
### player_profile.js
- Dynamic UI for status, workflow actions, CRM quick actions, instrument insights, and customer analytics.
- Personalized CRM actions and dashboard comments.
- Field logic for player level, newsletter, marketing opt-in, and communication preference.

### player_profile.py
- `autoname`: Generates unique player profile IDs.
- `validate`: Ensures required fields, compliance logic, and triggers CRM actions.
- `_block_marketing_emails`: Unsubscribes users under 13 and notifies parent/guardian.
- `_sync_email_group`: Syncs player to newsletter/marketing groups.
- `_sync_instruments_owned`: Updates owned instruments from linked profiles.
- `_calc_lifetime_value`: Calculates customer lifetime value from sales invoices.
- `on_update`: Handles CRM triggers, analytics, and notifications.
- `_notify_liked_instrument`: Notifies player when liked instrument is available.

## Doctypes Created/Updated/Modified
- Updates `Email Group Member`, `Instrument Profile`, `Sales Invoice`, `Customer`.
