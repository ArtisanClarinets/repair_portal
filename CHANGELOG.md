## 2025-07-25
### Added
- Created new child table Doctype: Player Equipment Preference (`istable: 1`) for condensing all player equipment preferences under one table. Includes mouthpiece, ligature, reed, barrel, and instrument fields, plus comments.
- Updated Player Profile Doctype to remove individual preference fields and replaced with a single Equipment Preference(s) table field.

### Notes
- File consolidation improves maintenance and UX. Old fields and child tables should be considered for removal after legacy data is migrated.
- Run `bench --site erp.artisanclarinets.com export-fixtures` after review.
