# Customer External Work Log (`customer_external_work_log`)

## Purpose
Child table for tracking service history performed by external shops (non-company). Customers report prior repairs, setups, or maintenance to provide complete instrument history.

## Schema Summary
- **Type:** Child Table (`istable: 1`)
- **Parent:** `Client Instrument Profile` (via `external_work_logs` field)

- **Key Fields:**
  - `instrument` (Link → Instrument): Instrument serviced
  - `service_date` (Date): When service was performed
  - `service_type` (Select): Inspection | Setup | Maintenance | Repair | Other
  - `service_notes` (Text): Description of work performed
  - `external_shop_name` (Data): Name of shop that performed work
  - `receipt_attachment` (Attach): Receipt or proof of service

## Business Rules

### Validation
1. **Required:** `instrument`, `service_date`
2. **Date logic:** `service_date` should not be in the future (advisory warning only)
3. **Service type:** Must be one of predefined options

### Data Entry
- Typically entered by customers via web form
- Technicians can add/edit during intake review
- Supports attachments (receipts, invoices)

## Client Logic (`customer_external_work_log.js`)
No form-level handlers required (child table row validation only).
All validation handled server-side.

## Server Logic (`customer_external_work_log.py`)
### Validation
- Ensures `service_date` is present
- Validates `service_type` against allowed values
- Warns if `service_date` is future-dated

## Data Integrity
- **Required:** `instrument`, `service_date`
- **Parent Field:** `external_work_logs` on `Client Instrument Profile`
- **Referential:** `instrument` must exist in Instrument DocType

## Usage Example
```python
# Add external work log to client profile
client_profile = frappe.get_doc('Client Instrument Profile', 'SER123')
client_profile.append('external_work_logs', {
    'instrument': 'INST-00001',
    'service_date': '2024-05-15',
    'service_type': 'Setup',
    'service_notes': 'Annual setup and pad replacement',
    'external_shop_name': 'Local Music Shop',
    'receipt_attachment': '/files/receipt.pdf'
})
client_profile.save()
```

## Test Plan
### Scenarios
1. **Add log with required fields** → Success
2. **Add log missing service_date** → ValidationError
3. **Add log with future date** → Warning
4. **Add log with invalid service_type** → ValidationError
5. **Add log with receipt attachment** → Attachment saved

### Fixtures
- Instrument: "INST-00001"
- Service Date: "2024-01-15"
- Service Type: "Repair"

## Changelog
- **2025-10-02:** Added mandatory headers, enhanced validation, date checks
- **2025-08-15:** Initial version
