# Instrument Condition Record (`instrument_condition_record`)

## Purpose
Child table for tracking instrument condition over time. Creates a timestamped snapshot of instrument health/state at various lifecycle points (intake, post-service, annual checkup, etc.).

## Schema Summary
- **Type:** Child Table (`istable: 1`, `is_child_table: 1`)
- **Parent:** `Instrument Profile` (via `condition_logs` field)
- **Naming:** By `instrument` field

- **Key Fields:**
  - `instrument` (Link → Instrument): Instrument being assessed
  - `condition` (Select): New | Good | Fair | Poor | Needs Repair
  - `date_of_record` (Date): When assessment was made
  - `recorded_by` (Link → User): User who recorded condition (auto-set)
  - `notes` (Text): Detailed condition notes
  - `workflow_state` (Select): Workflow State (optional)

## Business Rules

### Validation (`validate`)
1. **Required:** `instrument`, `condition`, `date_of_record`
2. **Auto-set:** `recorded_by` defaults to current user (`__user`)
3. **Date validation:** `date_of_record` should not be in future (advisory warning)

### Auto-population
- `recorded_by` automatically set to current session user
- `date_of_record` can default to today if not specified

## Client Logic
No dedicated `.js` file (child table; validation handled server-side).

## Server Logic (`instrument_condition_record.py`)
### Validation
- Enforces required fields
- Auto-sets `recorded_by` to `frappe.session.user`
- Validates `date_of_record` is not future-dated

### Usage Pattern
Typically created automatically during:
- Clarinet Intake (`after_insert`)
- Post-repair QA
- Annual maintenance checks

## Data Integrity
- **Required:** `instrument`, `condition`, `date_of_record`
- **Parent Field:** `condition_logs` on `Instrument Profile`
- **Referential:** `instrument` must exist; `recorded_by` must be valid User
- **Default:** `recorded_by` = `__user`

## Usage Example
```python
# Add condition record to profile
profile = frappe.get_doc('Instrument Profile', 'INSTPR-0001')
profile.append('condition_logs', {
    'instrument': 'INST-00001',
    'condition': 'Good',
    'date_of_record': frappe.utils.today(),
    'notes': 'Post-setup inspection: all pads sealing well, no mechanical issues'
})
profile.save()
```

## Workflow Integration (Optional)
- `workflow_state` field allows linking to workflow if needed
- Typically used for approval workflows on condition reports
- Not required for basic operation

## Permissions
Permissions inherited from parent `Instrument Profile`. Typical roles:
| Role              | Create | Read | Write |
|-------------------|--------|------|-------|
| Technician        | ✅     | ✅   | ✅    |
| Repair Manager    | ✅     | ✅   | ✅    |
| System Manager    | ✅     | ✅   | ✅    |

## Test Plan
### Scenarios
1. **Add record with all fields** → Success, `recorded_by` auto-set
2. **Add record missing instrument** → ValidationError
3. **Add record missing condition** → ValidationError
4. **Add record with future date** → Warning
5. **Add record without date** → Defaults to today
6. **Multiple records for same instrument** → All saved with timestamps

### Fixtures
- Instrument: "INST-00001"
- Condition: "Good"
- Date: Today

### Coverage Expectations
- **Target:** ≥75%
- **Critical paths:** Auto-set recorded_by, date validation

## Changelog
- **2025-10-02:** Added date validation, auto-set logic, comprehensive documentation
- **2025-07-03:** Initial version
