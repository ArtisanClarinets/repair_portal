# Inspection Report (`Inspection Report`)

Purpose: Capture inspection/QC results for instruments (serial-based and intake-based inspections). This DocType is referenced by stock-entry automation, workflows, and instrument profile lifecycle hooks.

Key fields:
- `inspection_date` (Date)
- `instrument_profile` (Link → Instrument Profile)
- `serial_no` (Data) — serial number for serial-based QC
- `stock_entry` (Link → Stock Entry) — origin of auto-created reports
- `inspection_type` (Select)
- `status` (Select) — `Scheduled`, `In Progress`, `Passed`, `Failed`, `Pending Review`
- `clarinet_intake_ref` (Link → Clarinet Intake) — original intake reference when migrating

Behavior:
- Default `status` is `Scheduled`.
- Lightweight validation ensures referenced `Instrument Profile` exists when provided.
