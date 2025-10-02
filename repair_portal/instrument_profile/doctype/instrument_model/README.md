# Instrument Model (`instrument_model`)

## Purpose
Master data defining instrument models. Combination of Brand + Model + Category + Body Material creates a unique instrument specification. Used for standardizing model data across the system.

## Schema Summary
- **Naming:** By `model` field
- **Key Fields:**
  - `brand` (Link → Brand): Manufacturer brand
  - `model` (Data): Model name/number
  - `instrument_category` (Link → Instrument Category): Type classification
  - `body_material` (Data): Primary body material (e.g., "Grenadilla", "Rosewood")
  - `instrument_model_id` (Data): Hidden unique ID

- **Links:**
  - `brand` → `Brand` (1:1, required) — manufacturer
  - `instrument_category` → `Instrument Category` (1:1, required) — type

## Business Rules

### Validation (`validate`)
1. **Required:** `brand`, `model`, `instrument_category`, `body_material`
2. **Uniqueness:** Combination of `brand` + `model` should be unique (advisory check)
3. **Active filters:** Only active brands and categories shown in dropdowns

### Naming
- Named by `model` field
- If duplicate models exist for different brands, append brand name for clarity

## Client Logic (`instrument_model.js`)
- **Set query filters:** Shows only active `Instrument Category` records
- **Duplicate detection:** On `brand` or `model` change, checks if same brand+model combination exists
- **Warning:** Shows alert if potential duplicate found (same brand+model)

## Server Logic (`instrument_model.py`)
Standard Document controller. No custom hooks beyond validation.

### Validation
- Ensures all required fields present
- Could add brand+model uniqueness constraint (currently advisory client-side)

## Data Integrity
- **Required:** `brand`, `model`, `instrument_category`, `body_material`
- **Unique:** `instrument_model_id` (hidden)
- **Naming:** By `model` field
- **Referential:** Links to Brand and Instrument Category must exist

## Usage Example
```python
# Create new model
model = frappe.get_doc({
    'doctype': 'Instrument Model',
    'brand': 'Buffet Crampon',
    'model': 'R13',
    'instrument_category': 'Bb Clarinet',
    'body_material': 'Grenadilla Wood'
})
model.insert()

# Query models by brand
models = frappe.get_all(
    'Instrument Model',
    filters={'brand': 'Buffet Crampon'},
    fields=['name', 'model', 'instrument_category']
)
```

## Permissions
| Role              | Create | Read | Write | Delete |
|-------------------|--------|------|-------|--------|
| System Manager    | ✅     | ✅   | ✅    | ✅     |
| Repair Manager    | ✅     | ✅   | ✅    | ❌     |
| Technician        | ❌     | ✅   | ❌    | ❌     |

## Test Plan
### Scenarios
1. **Create with all required fields** → Success
2. **Create missing brand** → ValidationError
3. **Create missing model** → ValidationError
4. **Create missing category** → ValidationError
5. **Create duplicate brand+model** → Warning (not blocked)
6. **Filter by active category** → Only active shown
7. **Quick entry** → Works via quick_entry flag

### Fixtures
- Brand: "Buffet Crampon"
- Model: "R13 Test"
- Category: "Bb Clarinet"
- Body Material: "Grenadilla"

### Coverage Expectations
- **Target:** ≥70%
- **Critical paths:** Required field validation, duplicate detection

## Common Models (Seed Data Examples)
| Brand            | Model      | Category     | Material      |
|------------------|------------|--------------|---------------|
| Buffet Crampon   | R13        | Bb Clarinet  | Grenadilla    |
| Buffet Crampon   | RC         | Bb Clarinet  | Grenadilla    |
| Selmer           | Privilege  | Bb Clarinet  | Grenadilla    |
| Yamaha           | YCL-650    | Bb Clarinet  | Grenadilla    |
| Leblanc          | Opus       | Bb Clarinet  | Grenadilla    |

## Bundled Data
Seed data available in: `repair_portal/instrument_setup/data/instrument_model_bundled.json`

## Changelog
- **2025-10-02:** Added duplicate detection, enhanced form logic, comprehensive README
- **2025-07-28:** Initial version
