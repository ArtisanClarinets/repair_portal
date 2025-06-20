# Planned Features: Service Planning

## Overview
Tools and automation for preventive maintenance, part lifespan, warranty, and communication with customers and schools.

### Features

#### a. Predictive Maintenance Scheduler
- Service Plan linked to Instrument
- Field: Play-hours (manual entry or external data import)
- ML Model/Script: Predicts next service, stores suggestion
- Calendar Sync: Google/Apple Calendar integration (OAuth, iCal feed)
- Auto-create calendar event/reminder for customer & tech

#### b. Component Lifespan Dashboard
- Component Odometer Table (instrument, pad/cork/spring, install date, cycles/uses, lifespan %)
- Visual bars/“odometers” per tracked part

#### c. Bulk-School Planner
- Band-director “Group” dashboard (many instruments to one school/contact)
- Bulk-PO/Batch service scheduler, PO generator

#### d. Warranty Countdown Widget
- UI widget: Remaining days calculation
- Prompt: Upsell for extended service as expiry nears

#### e. Automated Reminder Emails
- Email Drip Workflow:
  - Triggered on instrument intake, set by plan
  - 30/60/90 day custom templates
  - Personalization (instrument, user, last service)

---

*File last updated: 2025-06-19 / v1.0*