# Module: Repair Logging

## Purpose
Tracks and manages Repair Orders and Warranty data related to instrument service.

---

## Doctypes

### Repair Order
- Tracks the status of service operations.
- Fields: `customer`, `instrument`, `status`
- Workflow enabled via `status` field
- Submittable with lifecycle validation

### Warranty
- Tracks warranty expiry for each instrument.
- Fields: `instrument`, `warranty_expiry_date`, `coverage_notes`

---

## Updates

### 2025-06-20
- Created `Repair Order` Doctype with full schema and validation
- Created `Warranty` Doctype with expiry tracking
- Supports portal alert system via `get_pending_alerts` API
