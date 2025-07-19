# Lab Module – Artisan Clarinets ERPNext

## Purpose
Comprehensive scientific measurement, test, and analytics tracking for all instrument lab work. Supports leak tests, intonation, impedance, tone fitness, and scientific research. All data is structured for regulatory, ISO, and executive reporting.

## Key Doctypes
- **Measurement Session:** Root record for all instrument measurement/test events
- **Leak Test:** Scientific leak analysis for QA and diagnostics
- **Impedance Peak, Intonation Session, Tone Fitness:** Advanced acoustics/analytics

## Permissions
- **Lab Technician:** Full CRUD on measurements, sessions, and tests
- **Workshop Manager:** Approval and review of test data
- **Client:** Read-only portal access to their own results (when applicable)

## Workflows
All key records now have a `workflow_state` field for audit, review, and compliance. Typical states:
- Draft
- Awaiting Review
- Approved
- Archived

## Audit & Compliance
All records are linked to instrument, customer, and technician. Attachments and raw data fields support full traceability for scientific and regulatory requirements.

---
*Last updated: 2025-07-17 | Contact: dev@artisanclarinets.com*