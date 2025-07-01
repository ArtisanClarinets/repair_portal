# Repair Portal

## Update Log

### 2025-06-30: Inspection Unification
- **Clarinet Inspection** DocType is now fully unified under **Inspection Report**.
- Fields from Clarinet Inspection (preliminary_estimate, intake) are migrated and mapped.
- Status values unified and legacy reference fields added for traceability.
- All historic records will be accessible in Inspection Report.
- Clarinet Inspection is deprecated and set read-only after migration.

---

## Module Structure

(Existing structure remains unchanged)

## Next steps
- Run migration and remove old DocType from desk/menus.
- Confirm field mappings, test all inspection creation workflows, update any scripts/reports referencing the old doctype.
