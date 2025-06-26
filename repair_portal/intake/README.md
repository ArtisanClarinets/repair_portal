# Intake Module - MRW Artisan Clarinet Repair Portal

## Purpose
Handle complete instrument intake workflows including:
- Customer intake
- Loaner instrument issuance
- Consent forms
- Initial setup triggers
- Signature capture
- Digital document submission

## Key Features
- 📄 Clarinet Intake: master form linking all intake data
- 🔗 Links to Instrument Profile for service history
- 🖋️ Consent Form: signature and compliance checks
- 🎷 Loaner Instrument: PDF agreement auto-gen
- ⚙️ Initial Setup: created on intake submit
- 🌐 Web Form: customer self-submission portal
- ✅ Completion Validation: blocks submission unless all forms are ready
- 📝 Checklist options for case damage, tenon wear and loose rods
=======
- 🔍 Intake cannot be submitted without linking an Inspection


## Structure
- **Doctypes:** `clarinet_intake`, `customer_consent_form`, `loaner_instrument`
- **Page:** `intake_master_console`
- **Web Forms:** `clarinet_intake_request`
- **Templates:** loaner agreement HTML

## Automation
- Intake triggers setup
- Loaner issuance generates PDF
- Consent form includes digital signature

## Maintainers
Dylan Thompson / MRW Artisan Instruments

_Last updated: 2025-06-26_

### Change Log
- 2025-06-26 - Applied code formatting and added missing trailing newlines.
