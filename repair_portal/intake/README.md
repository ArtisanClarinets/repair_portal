# Intake Module - MRW Artisan Clarinet Repair Portal

## Purpose
Handle full intake pipeline:
- Customer details
- Consent forms
- Loaner issuance
- Setup prep
- Signatures
- OCR intake imports

## Key Features
- ✅ `Clarinet Intake`: primary customer/repair info form
- ✅ `Customer Consent Form`: signature, policies
- ✅ `Loaner Instrument`: PDF contract generator
- ✅ `OCR Upload`: scanned form → Intake via API
- ✅ `Intake Master Console`: summary dashboard
- ✅ `clarinet_intake_request` (Web Form)

## Automation
- Consent form and loaner auto-created
- OCR script parses image uploads

## Developer Info
- `/intake/api/import_handwritten_intake`
- PDF from `/loaner_agreement?name=...`

---
Last updated: 2025-07-03