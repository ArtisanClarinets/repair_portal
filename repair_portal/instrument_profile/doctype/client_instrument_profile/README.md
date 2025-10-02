# Client Instrument Profile (`client_instrument_profile`)

## Purpose
Customer-facing instrument profile created through web forms or customer portal. Allows customers to register their instruments with service history, photos, and repair preferences before technician verification.

## Schema Summary
- **Naming:** By `serial_no` field
- **Key Fields:**
  - `instrument_owner` (Link → Customer): Owner of the instrument
  - `serial_no` (Link → Serial No): ERPNext serial number
  - `instrument_model` (Data): Model name
  - `instrument_category` (Select): Type (Clarinet, Bass Clarinet, Contrabass Clarinet)
  - `verification_status` (Select): Pending | Approved | Rejected
  - `technician_notes` (Text): Technician review notes
  - `purchase_receipt` (Attach): Purchase documentation
  - `repair_preferences` (Small Text): Customer preferences for repairs
  - `ownership_transfer_to` (Link → Customer): Target customer for ownership transfer
  - `anonymize_for_research` (Check): Allow anonymized data sharing

- **Links:**
  - `instrument_owner` → `Customer` (1:1, required) — instrument owner
  - `serial_no` → `Serial No` (1:1, required) — ERPNext stock serial
  - `ownership_transfer_to` → `Customer` (optional) — transfer target

- **Child Tables:**
  - `external_work_logs` → `Customer External Work Log` — prior service history
  - `condition_images` → `Instrument Photo` — customer-uploaded photos
  - `consent_log` → `Consent Log Entry` — data use consent records

## Business Rules

### Validation (`validate`)
1. **Required fields:** `instrument_owner`, `instrument_model`, `serial_no` must be present
2. **Ownership transfer:**
   - Cannot transfer to same owner
   - Target customer must exist and be readable by current user
3. **Verification status:**
   - `Rejected` status requires `technician_notes`
   - Only Technician/Repair Manager/System Manager can change verification status

### Workflow
**States:** Pending → Approved | Rejected

- **Pending (default):** Awaiting technician review
- **Approved:** Creates/updates Instrument and Instrument Profile automatically
- **Rejected:** Requires technician notes; notifies customer

### Auto-creation on Approval (`_create_or_update_instrument_profile`)
When `verification_status` changes to `Approved`:
1. Check if `Instrument` exists for `serial_no`; if not, create it
2. Check if `Instrument Profile` exists for that instrument; if not, create it
3. Link customer as owner
4. Copy `repair_preferences` to `initial_condition_notes`

## Client Logic (`client_instrument_profile.js`)
- **Verification indicator:** Shows color-coded status (Pending=orange, Approved=green, Rejected=red)
- **Transfer Ownership button:** (Approved only) Prompts for new customer and sets `ownership_transfer_to`
- **Auto-clear transfer:** Clears `ownership_transfer_to` if `instrument_owner` changes

## Server Logic (`client_instrument_profile.py`)
### Public Methods
None (standard CRUD only; no whitelisted endpoints)

### Hooks
- `validate`: Enforces required fields, ownership logic, verification permissions
- `on_update`: Triggers instrument/profile creation on approval

## Data Integrity
- **Unique:** `serial_no` (enforced by autoname)
- **Required:** `instrument_owner`, `instrument_model`, `serial_no`, `instrument_category`, `verification_status`
- **Defaults:** `verification_status` = 'Pending', `anonymize_for_research` = 0
- **Referential:** Must link to existing Customer and Serial No; creates Instrument/Profile on approval

## Permissions
| Role              | Create | Read | Write | Delete |
|-------------------|--------|------|-------|--------|
| Customer          | ✅     | ✅   | ✅    | ❌     |
| Technician        | ❌     | ✅   | ✅    | ❌     |
| Repair Manager    | ❌     | ✅   | ✅    | ❌     |
| System Manager    | ✅     | ✅   | ✅    | ✅     |

## Test Plan
### Scenarios
1. **Create with all required fields** → Success
2. **Create missing owner** → ValidationError
3. **Reject without notes** → ValidationError
4. **Approve as Customer** → PermissionError
5. **Approve as Technician** → Creates Instrument + Profile
6. **Transfer ownership to same owner** → ValidationError
7. **Upload images via `condition_images`** → Stored correctly
8. **Anonymize toggle** → Saves correctly

### Fixtures
- Customer: "Test Owner"
- Serial No: "TEST123"
- Instrument Model: "R13"
- Instrument Category: "Clarinet"

### Coverage Expectations
- **Target:** ≥80%
- **Critical paths:** Validation, approval workflow, instrument/profile creation

## Changelog
- **2025-10-02:** Added comprehensive validation, auto-creation logic, ownership transfer validation
- **2025-06-15:** Initial version with basic verification workflow
