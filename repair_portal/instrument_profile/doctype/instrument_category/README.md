# Instrument Category (`instrument_category`)

## Purpose
Master data for instrument categories/types. Defines the classification system for instruments (e.g., "Bb Clarinet", "Bass Clarinet", "A Clarinet"). Used across the system for filtering, reporting, and categorization.

## Schema Summary
- **Naming:** By `title` field (unique)
- **Key Fields:**
  - `title` (Data): Category name (e.g., "Bb Clarinet")
  - `description` (Small Text): Detailed description
  - `is_active` (Check): Active/inactive toggle

- **Links:** None (master data)

## Business Rules

### Validation (`validate`)
1. **Uniqueness:** `title` must be unique across all categories
2. **Required:** `title` must be present
3. **Default:** `is_active` defaults to 1 (checked)

### Active Status
- **Active categories** appear in dropdown filters
- **Inactive categories** hidden from new data entry but preserved for existing records
- Deactivating a category does not break existing instrument links

## Client Logic (`instrument_category.js`)
- **Active indicator:** Shows green/red headline based on `is_active`
- **Deactivation warning:** Warns user about potential impact on existing instruments
- No complex validation needed (simple CRUD)

## Server Logic (`instrument_category.py`)
Standard Document controller. No custom hooks or whitelisted methods.

### Validation
- Enforces `title` uniqueness via DocType schema
- No additional server-side validation required

## Data Integrity
- **Unique:** `title` (enforced by autoname)
- **Required:** `title`
- **Defaults:** `is_active` = 1
- **Referential:** Used by `Instrument`, `Instrument Model`, `Instrument Profile`

## Usage Example
```python
# Create new category
category = frappe.get_doc({
    'doctype': 'Instrument Category',
    'title': 'Alto Clarinet',
    'description': 'Alto clarinet in Eb',
    'is_active': 1
})
category.insert()

# Deactivate category
frappe.db.set_value('Instrument Category', 'Alto Clarinet', 'is_active', 0)
```

## Permissions
| Role              | Create | Read | Write | Delete |
|-------------------|--------|------|-------|--------|
| System Manager    | ✅     | ✅   | ✅    | ✅     |
| Technician        | ✅     | ✅   | ✅    | ❌     |
| Repair Manager    | ✅     | ✅   | ✅    | ❌     |

## Test Plan
### Scenarios
1. **Create with unique title** → Success
2. **Create with duplicate title** → UniqueError
3. **Create without title** → ValidationError
4. **Toggle is_active** → Updates correctly
5. **Deactivate category with linked instruments** → Category deactivated, instruments unaffected
6. **Filter active categories** → Only active shown

### Fixtures
- Title: "Test Category Bb"
- Description: "Test category for Bb clarinets"
- is_active: 1

### Coverage Expectations
- **Target:** ≥70%
- **Critical paths:** Title uniqueness, active/inactive toggle

## Common Categories (Seed Data)
- Bb Clarinet
- A Clarinet
- Eb Clarinet
- Bass Clarinet
- Alto Clarinet
- Contrabass Clarinet

## Changelog
- **2025-10-02:** Added active status warning, enhanced form logic, comprehensive README
- **2025-07-19:** Initial version
