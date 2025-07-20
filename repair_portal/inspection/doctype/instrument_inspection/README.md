# Instrument Inspection Doctype

## Purpose
This DocType tracks all inspections performed on instruments (clarinets) at any stage in their lifecycle, including:
- **New Inventory Intake**
- **Repair**
- **Maintenance**
- **Quality Assurance (QA)**
- **Other Special Cases**

The inspection record is a critical, event-driven document that collects not only QC and findings, but also deep, persistent instrument specifications needed for building and updating the Instrument Profile.

## Key Business Logic & Automation
- **Validation:**
  - Serial number must be unique per inspection.
  - For `New Inventory` type, Manufacturer, Model, Key, and Wood Type are required.
  - Customer and Estimate fields are not allowed on New Inventory.
- **Automation:**
  - On submit, all detailed specs and media fields (e.g. Body Material, Bore, Pad Type, Photos) are synced to the Instrument Profile DocType.
  - If no Instrument Profile exists for the serial number, one is automatically created.
  - Robust error handling and logging (`frappe.log_error`) for traceability.
- **Field Coverage:**
  - Collects deep specifications and media (see full JSON for field list).
  - Provides child tables for photos, media, and accessories.

## UX Pattern
- Only essential details are required during fast intake.
- Full detailed specs and persistent fields are captured at inspection, ensuring the Profile is always up-to-date with the latest findings and configuration.

## Compliance & Standards
- Frappe/ERPNext v15 compliant.
- Security: Follows role-based permissions for Technician, Service Manager, and System Manager.
- Error handling: All critical operations log tracebacks on failure for audit.

---

**Automation implemented in:**
- `instrument_inspection.py`: Validation, profile syncing, exception logging.

**For detailed logic, see:**
- This directory's `.json` and `.py` files.
- The Instrument Profile doctype README for profile sync details.
