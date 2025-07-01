# Instrument Profile Module

## Summary of 2025-07-01 Patch

### New & Enhanced Features
- **Document History (Traceability):**
  - Instrument Profile now links a new child table: **Instrument Document History** for event-level logging.
  - Tracks all Setup, Inspection, Repair, and Ownership Transfer events. Fully auditable.
- **Batch Archive / Transfer Tool Ready:**
  - Profiles support archiving; logic in controller. Bulk tools can leverage the new `is_archived` field.
- **Profile Transparency & QR Portal:**
  - Profiles have unique public URLs for QR code display and client transparency.
  - Ready for both public (guest) and authenticated client portal display.
- **Serial Number as Primary ID:**
  - Serial is unique, required, and appears as first column in list views. Prevents duplicates.
- **Deletion/Archiving:**
  - All deletions use soft archive for auditability.

### Compliance, Roles & Permissions
- All fields/logic align with Frappe v15 standards and Fortune 500-grade validation.
- Permissions: System Manager, QA Tech, Technician
- Title field: Serial Number

### Next Steps
- Migrate/match old Instrument Profile data as needed.
- Expand client portal: enable file/media timeline, QA certificate display, etc.

---

_This README is always updated with new logic, features, and patch notes._

_Last updated: 2025-07-01_
