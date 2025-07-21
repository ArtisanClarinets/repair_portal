## 2025-07-21
- Refactor: Clarinet Intake Settings now uses a child table for Brand Mapping Rules (`brand_mapping_rules`) instead of a raw JSON code field.
- Added new child DocType: Brand Mapping Rule (fields: from_brand, to_brand).
- Updated clarinet_intake_settings.py to remove JSON validation, now reads mapping as a child table.
- Updated clarinet_intake.py: all brand mapping logic now references the table, not JSON.
- No data migration script needed if old brand mapping not used. If needed, a one-off patch should map existing JSON to table rows.
