# Brand Mapping Rule (`brand_mapping_rule`)

## Purpose
The Brand Mapping Rule DocType defines how external or alternate brand names are mapped to standardized brand identifiers within the Repair Portal. This ensures consistency in intake processing, reporting, and instrument profile linkage.

## Schema Summary
- **Naming:** Auto-assigned (system managed)
- **DocType Type:** Child Table (`istable: 1`)
- **Key Fields:**
  - `from_brand` (Data, Required): Original brand name (e.g., "Buffet-Crampon Paris")
  - `to_brand` (Data, Required): Standardized mapped brand (e.g., "Buffet")

## Business Rules
- Each mapping links one external brand name to a standardized brand.
- Duplicate mappings are not allowed; each `(from_brand, to_brand)` pair must be unique.
- Used in intake workflows to automatically normalize brand values.

## Python Controller Logic
File: `brand_mapping_rule.py`

- **Class:** `BrandMappingRule(Document)`
- **Methods:**
  - `validate()`: Ensures that `from_brand` and `to_brand` are provided and calls duplicate-check.
  - `validate_unique_mapping()`: Prevents saving if the same mapping already exists.

### Example Logic
```python
if not self.from_brand:
    frappe.throw("From Brand is required")

if not self.to_brand:
    frappe.throw("To Brand is required")

if frappe.db.exists("Brand Mapping Rule", {
    "from_brand": self.from_brand,
    "to_brand": self.to_brand,
    "name": ["!=", self.name],
}):
    frappe.throw(f"A mapping from '{self.from_brand}' to '{self.to_brand}' already exists.")
```

## Client-Side Script
- No JavaScript controller currently exists.
- Potential enhancements:
  - Auto-suggest known brands when typing `from_brand`.
  - Validation warning if `from_brand` and `to_brand` are identical.

## Integration Points
- **Clarinet Intake**: Ensures brand normalization when new instruments are logged.
- **Reports**: Provides standardized brand names for consistent analytics.
- **Inventory**: Maps alternate names to unified brand references.

## Validation Standards
- `from_brand`: Required, non-empty string.
- `to_brand`: Required, non-empty string.
- Duplicate `(from_brand, to_brand)` pairs not allowed.

## Usage Examples
- `from_brand: Buffet-Crampon Paris → to_brand: Buffet`
- `from_brand: Selmer USA → to_brand: Selmer`

## Changelog
- **2025-08-16**: Initial documentation created for schema, logic, and usage.

## Dependencies
- **Frappe Framework**: Child table validation and uniqueness enforcement.
- **Parent DocType**: Used inside Clarinet Intake and related intake doctypes.