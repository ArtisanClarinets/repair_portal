# Instrument Profile Doctype

## Purpose
The Instrument Profile DocType is the **single source of truth** for every unique clarinet (or instrument) in your system. Think of it as a "social media profile" for each instrument, aggregating its complete story:
- Specifications and configuration (core and evolving)
- All service, repair, and ownership history
- Commercial, appraisal, warranty, and status data
- Media gallery (hero images, marketing, service photos, audio/video demos)
- Analytics tags and staff notes

This persistent record enables provenance, customer engagement, analytics, and premium resale value.

## Key Business Logic & Automation
- **Aggregation:** Pulls data from Intake, Inspections, Setups, Service Logs, and external sources to build a 360-degree view.
- **Specs Sync:** On submission of an Instrument Inspection, deep/persistent specs and media are pushed here and saved.
- **Lifecycle Automation:**
  - Links to all associated events (repairs, service, QA, ownership, warranty) as child tables.
  - Maintains and displays all logs, photos, and provenance as the instrument's "timeline."
- **Warranty Sync:**
  - Always reflects the current warranty expiration (pulled from Serial No in ERPNext).
- **Error Handling:**
  - All background sync and auto-link actions are logged for exception traceability.

## Field Structure
- **Specs:** Core profile (model, year, material, keywork, bore, pads, etc.)
- **Lifecycle/Status:** Real-time status, location, acquisition/service/sales history
- **Media Gallery:** Images, audio/video, service photo logs
- **Associated Items:** Accessories, barrels, cases, bells (see child tables)
- **Relational Links:** Current owner, ownership history, technician/service logs, followers/likes
- **Analytics & Notes:** Tags, staff/internal notes, advanced filtering

## Compliance & Standards
- Frappe/ERPNext v15 compliant
- Strict permissions: Only system managers, repair managers can update; owners and technicians have view rights
- Field coverage matches the strategic table in the onboarding doc
- Full audit/compliance for provenance and warranty

---
**Automation implemented in:**
- `instrument_profile.py` (ERPNext sync, logs, warranty, all linked table aggregation)
- Inspection and other event doctypes (push spec/media changes on submit)

**For detailed field map and sync logic, see:**
- This directory's `.json` and `.py` files
- The Instrument Inspection doctype README for how events push updates here
