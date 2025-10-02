# Instrument Serial Number (`instrument_serial_number`)

## Purpose
Canonical registry for instrument serial numbers. Handles normalization, duplicate detection, verification status, and linkage to Instrument records. Supports photo documentation of serial stamps/engravings and shop-applied scan codes.

## Schema Summary
- **Naming:** By `serial` field (as stamped on instrument)
- **Document Type:** Setup
- **Key Fields:**
  - `serial` (Data): Raw serial as stamped/engraved (required, searchable)
  - `normalized_serial` (Data): Uppercased, alphanumeric-only form for matching (hidden, indexed)
  - `serial_source` (Select): Stamped | Engraved | Etched | Label/Sticker | Handwritten | Unknown
  - `scan_code` (Data): Shop-applied barcode/QR code (optional)
  - `photo` (Attach Image): Photo of serial stamp
  - `instrument` (Link → Instrument): Linked instrument record
  - `erpnext_serial_no` (Link → Serial No): ERPNext inventory serial (optional)
  - `verification_status` (Select): Unverified | Verified by Technician | Customer Reported | Disputed
  - `verified_by` (Link → User): Who verified (auto-set)
  - `verified_on` (Datetime): When verified (auto-set)
  - `status` (Select): Active | Deprecated | Replaced | Error
  - `duplicate_of` (Link → Instrument Serial Number): If this is a duplicate, link to canonical record

## Business Rules

### Normalization (`_normalize`)
- Converts `serial` to uppercase, removes punctuation/spaces → `normalized_serial`
- Uses `repair_portal.utils.serials.normalize_serial()` (single source of truth)
- Executed in `before_insert` and `validate`

### Uniqueness Validation (`_validate_uniqueness`)
Complex duplicate detection across instruments and brands:

1. **Same Instrument:** Block if same instrument already has this normalized serial
2. **Different Instruments, Same Brand:** Block if another instrument with same brand has this serial
3. **Different Instruments, Different Brands:** Allow but advise (different makers can share serial patterns)
4. **Unlinked Duplicates:** Block if another unlinked ISN has same normalized serial (ambiguous)
5. **Advisory for Cross-Brand:** Show warning if linked records exist for other brands

### Verification (`_set_verification_meta`)
- When `verification_status` = 'Verified by Technician':
  - Auto-set `verified_by` to current user
  - Auto-set `verified_on` to now

### Instrument Linkage
- **After Insert:** Calls `utils.serials.attach_to_instrument()` to set `Instrument.serial_no` → this ISN
- **On Update:** Re-syncs linkage if `instrument` field changes
- **Idempotent:** Safe to call multiple times

## Client Logic (`instrument_serial_number.js`)
- **Duplicate advisory:** Debounced check on `serial_no`, `brand`, `model`, `year_estimate` changes
- **Create Setup button:** Quick action to create `Clarinet Initial Setup` from ISN
- **Ownership toggle:** Shows/hides owner fields based on `ownership_type`

## Server Logic (`instrument_serial_number.py`)

### Public Methods
```python
@frappe.whitelist()
def attach_to_instrument(self, instrument: str)
```
Links this ISN to an Instrument and sets `Instrument.serial_no` when Link field exists.

### Lifecycle Hooks
- `before_insert()`: Normalize serial
- `validate()`: Normalize, validate requireds, check uniqueness, set verification meta
- `after_insert()`: Attach to instrument if set
- `on_update()`: Re-attach to instrument if changed

## Utility Module (`repair_portal.utils.serials`)
Single source of truth for all ISN operations:

- `normalize_serial(s)`: Returns uppercase alphanumeric-only string
- `ensure_instrument_serial(...)`: Idempotent ISN creation
- `find_by_serial(serial_input)`: Lookup by normalized form
- `find_by_scan_code(scan_code)`: Lookup by shop barcode
- `attach_to_instrument(isn_name, instrument)`: Link ISN to Instrument
- `merge_serials(primary, duplicate)`: Merge duplicate ISNs
- `backfill_normalized_serial()`: One-time migration for legacy data

## Data Integrity
- **Required:** `serial`
- **Unique:** `serial` (via naming), `normalized_serial` (indexed for fast lookup)
- **Indexes:** `serial`, `normalized_serial` (add via patch if not present)
- **Referential:** `instrument` → Instrument, `erpnext_serial_no` → Serial No

## Usage Example
```python
from repair_portal.utils.serials import ensure_instrument_serial

# Create or get ISN
isn_name = ensure_instrument_serial(
    serial_input='A-123456',
    instrument='INST-00001',
    scan_code='QR-789',
    status='Active',
    serial_source='Stamped',
    verification_status='Verified by Technician'
)

# Find by serial
isn = frappe.get_doc('Instrument Serial Number', isn_name)
print(isn.normalized_serial)  # 'A123456'
```

## Permissions
| Role              | Create | Read | Write | Delete |
|-------------------|--------|------|-------|--------|
| Technician        | ✅     | ✅   | ✅    | ❌     |
| Repair Manager    | ✅     | ✅   | ✅    | ✅     |
| Service Manager   | ✅     | ✅   | ✅    | ✅     |
| System Manager    | ✅     | ✅   | ✅    | ✅     |

## Test Plan
### Scenarios
1. **Create with unique serial** → Success, `normalized_serial` set
2. **Create duplicate for same instrument** → ValidationError
3. **Create duplicate for same brand, different instrument** → ValidationError
4. **Create duplicate for different brand** → Warning only
5. **Create unlinked duplicate** → ValidationError
6. **Verify as technician** → `verified_by` and `verified_on` auto-set
7. **Attach to instrument** → `Instrument.serial_no` updated
8. **Normalize 'A-123 456'** → 'A123456'
9. **Find by serial** → Returns correct ISN
10. **Merge duplicates** → Primary retained, duplicate deprecated

### Fixtures
- Serial: "TEST-123"
- Normalized: "TEST123"
- Instrument: "INST-00001"
- Brand: "Buffet Crampon"

### Coverage Expectations
- **Target:** ≥85%
- **Critical paths:** Normalization, uniqueness validation, verification workflow, instrument linkage

## Workflow States
- **Un-Linked** (Yellow): ISN created but not linked to Instrument
- **Linked** (Green): ISN linked to Instrument
- **Retired** (Gray): Deprecated or replaced

## Integration Points
- **Clarinet Intake:** Auto-creates ISN on intake insert
- **Instrument Profile:** Syncs serial display from ISN
- **Inventory:** Optional link to ERPNext Serial No for stock tracking

## Changelog
- **2025-10-02:** Comprehensive README, enhanced validation documentation
- **2025-08-14:** Refined duplicate detection, added brand-aware uniqueness
- **2025-08-13:** Initial version with normalization and verification
