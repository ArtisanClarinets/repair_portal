# Repair Planned Material & Repair Actual Material  
*Frappe/ERPNext v15 Child Table Doctypes*

---

## Overview
These two child Doctypes represent the **materials used in a clarinet repair workflow**:

| Doctype | Purpose |
|---------|--------|
| **Repair Planned Material** | Materials the technician *expects* to use when preparing a repair quotation or plan. |
| **Repair Actual Material** | Materials that were *actually consumed* and recorded via submitted **Stock Entry** documents. |

Both Doctypes are designed to integrate seamlessly with the **Repair Order** workflow and with **ERPNext Stock & Accounts** modules.

---

## Key Features

### Shared Characteristics
- **Editable Grid** child tables for quick inline entry inside a Repair Order.
- Automatic **UOM backfill** from the selected `Item`’s `stock_uom`.
- Automatic **amount calculation** (`qty × rate` or `qty × valuation_rate`) both client-side and server-side for consistent reporting.
- Server-side validation to ensure numeric fields are normalized and read-only totals are enforced.

### Planned vs Actual
| Feature | Planned | Actual |
|---------|--------|-------|
| Rate Source | Technician-entered or fetched from Item Price | Pulled from submitted Stock Entry valuation |
| Purpose | Estimate costs before work begins | Capture true cost after work is complete |
| Typical Use | Repair quotation and planning | Final billing & cost analysis |

---

## Directory Layout

```

repair\_portal/
└─ repair/
└─ doctype/
├─ repair\_planned\_material/
│  ├─ repair\_planned\_material.json
│  ├─ repair\_planned\_material.py      # Server-side validation & helpers
│  └─ repair\_planned\_material.js      # Client grid logic
└─ repair\_actual\_material/
├─ repair\_actual\_material.json
├─ repair\_actual\_material.py       # Server-side validation & helpers
└─ repair\_actual\_material.js       # Client grid logic

````

---

## Server Logic Highlights

| File | Key Responsibilities |
|------|----------------------|
| `repair_planned_material.py` | Ensures UOM defaults from Item, computes `amount = qty × rate`, backfills description if empty. |
| `repair_actual_material.py`  | Ensures UOM defaults, computes `amount = qty × valuation_rate`, normalizes numerics, mirrors Stock Entry rows. |

All computations use Frappe’s `flt()` for safe float conversion.

---

## Client Logic Highlights

| File | Key Responsibilities |
|------|----------------------|
| `repair_planned_material.js` | Updates `amount` on `qty`/`rate` change, pulls UOM and a concise description when `item_code` is selected. |
| `repair_actual_material.js`  | Updates `amount` on `qty`/`valuation_rate` change, backfills UOM when `item_code` is selected. |

These scripts run inside the parent form’s grid to keep the user interface responsive and in sync with server calculations.

---

## Integration with Repair Order

* **Repair Planned Material** rows can be added during quotation or planning.  
* **Repair Actual Material** rows are **mirrored automatically** when a technician submits a **Stock Entry (Material Issue)** referencing the Repair Order, ensuring the accounting ledger remains the source of truth.

---

## Best Practices & Security

- All calculations are duplicated server-side to prevent tampering with read-only totals.
- UOM and Item metadata are fetched from ERPNext core doctypes (`Item`, `UOM`) ensuring single source of truth.
- Designed and tested for **Frappe/ERPNext v15**; follows Frappe’s naming conventions and DocType JSON schema.

---

## Maintenance & Testing

1. **Apply migrations**
   ```bash
   bench --site <your-site> migrate
   bench build
   bench --site <your-site> clear-cache
````

2. **Unit Tests**
   Add or extend tests in `repair_portal/repair/tests/` to verify:

   * Automatic UOM population
   * Correct amount calculations
   * Successful mirroring of actual materials from Stock Entries.

---

## License

© 2025 MRW Artisan Instruments — All rights reserved.
Released as part of the **Repair Portal** Frappe App under your standard project license.


