# Artisan Clarinets — Instrument Profile System: Onboarding Guide

## Overview
Welcome to the most advanced instrument lifecycle and provenance platform in the industry! This Frappe/ERPNext app transforms every clarinet into a data-driven "social media profile," capturing its full story from first intake to every service, sale, and owner.

**Who Should Use This Guide:**
- New staff (techs, sales, admin)
- Consultants and developers
- QA and audit teams

---

## What is an Instrument Profile?
A persistent record for each unique instrument, acting as the single source of truth for:
- Technical specifications and configuration (body, bore, keys, pads, etc.)
- Full lifecycle logs (intake, inspection, repairs, QA, sales)
- Ownership and technician history
- Commercial data (pricing, warranty, appraisals)
- Media gallery (photos, audio, video)
- Analytics, tags, and notes for smart filtering, marketing, and resale

## Workflow Summary
1. **Intake:** Fast entry at the point of arrival—just the basics.
2. **Inspection:** Tech performs deep, detailed documentation and captures full specs, media, and accessories.
3. **Profile Update:** All new data and media are pushed to the Instrument Profile, which grows richer over time.
4. **Service/Repair:** Every new work order is logged, with before/after photos and detailed findings.
5. **Resale/Ownership:** Profile reflects sales, transfers, and provenance.
6. **Analytics/Engagement:** Marketing uses "Followers/Likes" and tags for targeted outreach; sales and techs see 360° history for intelligent recommendations.

## Why This Matters
- **Provenance & Value:** Buyers can see every detail, service, and owner—critical for vintage, professional, and consignment sales.
- **Customer Engagement:** "Likes" and history let us target warm leads and nurture long-term client relationships.
- **Audit & Compliance:** Every action and field is tracked for quality, warranty, and compliance audits.
- **Competitive Edge:** No other dealer offers this level of transparency, detail, or data-driven recommendations.

---

## Key DocTypes
- **Instrument Profile:** The master record.
- **Instrument Inspection:** Event-driven collection of specs, findings, and media. Triggers profile updates.
- **Instrument Photo/Media/Accessory:** All supporting tables for photos, media, and current/historical accessories.

## Developer Handoff
- See each DocType's `README.md` for logic, automation, and field details.
- All automation is in Python controllers, following Fortune-500 and Frappe v15 standards.
- Use the built-in error logs for any exception tracebacks.

## Getting Started
- Log in as a Technician or Service Manager.
- Intake new instrument (minimal required fields).
- Open or create an Instrument Inspection to add deep data and upload media.
- Check the Instrument Profile—watch it update!

---

*For more detail, see each directory's README or ask Priscilla (the virtual Frappe engineer).*