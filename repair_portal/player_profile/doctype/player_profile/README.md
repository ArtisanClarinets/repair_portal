# Player Profile Doctype

## Purpose
The Player Profile Doctype is the comprehensive, Fortune-500-grade CRM record for every musician, client, or customer in your ecosystem. It provides a single, persistent source of truth for each player's identity, musical background, equipment preferences, service history, and relationship with the store. Used in tandem with Instrument Profile, it empowers hyper-personalized sales, service, marketing, and community building.

---

## Field Map & Coverage

- **Core Identity & Contact**: Full Name, Preferred Name, Email, Phone, Mailing Address, Creation Date
- **Musical Profile**: Player Level, Playing Styles, Affiliation/Organization, Teacher/Mentor
- **Equipment Preferences**: Mouthpieces, Ligatures, Reed Brand/Model/Strength, Barrels, Preferred Instruments
- **Service & Setup Preferences**: Key Height, Spring Tension, Pad Type, G#/A Connection, Intonation Notes, Technician Notes
- **Store Relationship**: Owned/Liked Instruments, Purchase & Service History, Last Visit Date, Customer Lifetime Value
- **Marketing & Communication**: Communication Preference, Newsletter Subscription, Targeted Marketing Opt-in
- **Internal Analytics**: Staff Notes (running log), Referral Source

All fields and tables are fully permissioned per best practices, with privacy and compliance at every layer.

---

## Key Business Logic & Automations

- **Auto-generates unique Player Profile ID** (PLAYER-XXXXX)
- **Enforces required fields and contact compliance**
- **COPPA/GDPR Compliance**: Under-13 users are unsubscribed and parent notified
- **Newsletter & Opt-in Sync**: Adds/removes player from marketing lists as needed
- **Instruments Owned & Liked**: Linked to Instrument Profile for full provenance
- **Customer Lifetime Value**: Auto-calculated from linked Sales Invoices
- **CRM Triggers**: Notifies player if a liked instrument becomes available
- **Personalization**: Preferences/notes available to techs at every service touchpoint

---

## User Experience & UI Features

- **Dynamic UI**: Student/Pro fields shown based on Player Level
- **Action Buttons**: Email, show owned/liked instruments, quick CRM actions
- **Insights**: CLV and last visit always visible to staff
- **Staff Notes**: Permanent, append-only analytics log

---

## Permissions & Security

- **Role-based permissions** for System Manager, Technician, Repair Manager, and Player
- **All PII fields** secured and never exposed to unauthorized users
- **All email and marketing preferences** opt-in and consent-driven
- **Audit-ready**: All changes tracked, errors logged

---

## Technical Compliance
- Frappe/ERPNext v15, PEP8, field naming conventions
- No business logic on client side—only UI triggers
- No direct database writes from JS
- Data structure matches latest Fortune-500 and music CRM best practices

---

## Related Files
- `player_profile.json`: Doctype schema
- `player_profile.py`: Backend controller/business logic
- `player_profile.js`: Dynamic UI logic & workflow
- `README.md`: (This file)
- `test_player_profile.py`: Automated tests for CRUD, linkage, and analytics

---

## Support & Documentation
Questions? Contact the ERP Team, see Desk module help, or refer to `/CHANGELOG.md` for business rule changes. All tech debt is tracked and reviewed quarterly.
