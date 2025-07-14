### v1.5.1 - Serial Number Integration

- 🔗 `Instrument Profile` now integrates with ERPNext's `Serial No`:
  - New Link field: `erpnext_serial_no` (hidden, staff-only)
  - Auto-creates missing `Serial No` records based on `serial_number`
  - Validates model alignment
  - All sync actions log exceptions with `frappe.log_error()`

