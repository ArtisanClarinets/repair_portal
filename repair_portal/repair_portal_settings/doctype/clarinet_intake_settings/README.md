## Doctype: Clarinet Intake Settings

### 1. Overview and Purpose

**Clarinet Intake Settings** is a doctype in the **Repair Portal Settings** module that manages and tracks related business data.

**Module:** Repair Portal Settings
**Type:** Master/Standard Document

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `default_item_group` | Link (Item Group) | Default: `Clarinets` |
| `default_inspection_warehouse` | Link (Warehouse) | Default Inspection Warehouse |
| `buying_price_list` | Link (Price List) | Default: `Standard Buying` |
| `selling_price_list` | Link (Price List) | Default: `Standard Selling` |
| `stock_uom` | Link (UOM) | Default: `Nos` |
| `require_inspection` | Check | Default: `1` |
| `auto_create_initial_setup` | Check | Default: `1` |
| `notify_on_stock_issue` | Check | Default: `1` |
| `auto_normalize_brand` | Check | Default: `0` |
| `inspection_type_inventory` | Data | Default: `Initial Inspection` |
| `inspection_type_repair` | Data | Default: `Arrival Inspection` |
| `supplier_code_prefix` | Data | Supplier Code Prefix |
| `intake_naming_series` | Data | Default: `INV-.#####` |
| `intake_id_pattern` | Data | Default: `CI-.{YYYY}.-.#####` |
| `brand_mapping_rules` | Table (Brand Mapping Rule) | Brand Mapping Rules |
| `auto_create_consent_form` | Check | Default: `0`. When enabled, automatically creates a Consent Form for Repair/Maintenance intakes |
| `default_consent_template` | Link (Consent Template) | Template used for auto-created consent forms |
| `consent_required_for_intake_types` | Select (Repair
Maintenance
Repair and Maintenance) | Default: `Repair and Maintenance`. Which intake types require consent forms |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`clarinet_intake_settings.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving

**Custom Methods:**
- `get_intake_settings()`: Custom business logic method

#### Frontend Logic (JavaScript)

*No JavaScript file found. This doctype uses standard Frappe form behavior.*

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Links to **Item Group** doctype via the `default_item_group` field (Default Item Group)
- Links to **Warehouse** doctype via the `default_inspection_warehouse` field (Default Inspection Warehouse)
- Links to **Price List** doctype via the `buying_price_list` field (Buying Price List)
- Links to **Price List** doctype via the `selling_price_list` field (Selling Price List)
- Links to **UOM** doctype via the `stock_uom` field (Stock UOM)
- Has child table **Brand Mapping Rule** stored in the `brand_mapping_rules` field
- Links to **Consent Template** doctype via the `default_consent_template` field (Default Consent Template)

### 5. Critical Files Overview

- **`clarinet_intake_settings.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`clarinet_intake_settings.py`**: Python controller implementing business logic, validations, and lifecycle hooks

---

*Last updated: 2025-10-04*
