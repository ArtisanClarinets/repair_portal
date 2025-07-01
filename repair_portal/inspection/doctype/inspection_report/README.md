# Inspection Report (Unified)

## Update: 2025-06-30 — Unified with Clarinet Inspection
- Added: `preliminary_estimate`, `clarinet_intake_ref`, and `legacy_clarinet_inspection_id` fields for complete migration.
- Status values unified for both legacy and new records.
- All Clarinet Inspection records will be migrated here for single-source reporting.
- Legacy data lineage maintained in `legacy_clarinet_inspection_id`.

**IMPORTANT:**
- After migration, all new inspections should use only Inspection Report.
- Old Clarinet Inspection DocType is deprecated and will be archived.

---

## Migration Plan
1. All Clarinet Inspection records migrated to this DocType.
2. All fields mapped, with legacy references kept.
3. Reports, dashboards, and analytics unified.
4. Old DocType set as read-only and removed from menus.

See migration script and change log for full audit trail.
