## Doctype: Clarinet Intake Settings

### 1. Overview and Purpose

**Clarinet Intake Settings** centralises configuration for the intake pipeline:
brand normalisation, automation toggles, consent defaults, and the SLA target
surfaced to coordinators. The DocType lives under the **Repair Portal Settings**
module and is a single (global) record.

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `default_item_group` | Link (Item Group) | Default: `Clarinets` |
| `default_inspection_warehouse` | Link (Warehouse) | Default inspection warehouse |
| `buying_price_list` | Link (Price List) | Default: `Standard Buying` |
| `selling_price_list` | Link (Price List) | Default: `Standard Selling` |
| `stock_uom` | Link (UOM) | Default: `Nos` |
| `require_inspection` | Check | Require instrument inspection on intake |
| `auto_create_initial_setup` | Check | Auto-create Clarinet Initial Setup |
| `notify_on_stock_issue` | Check | Notify users on stock issues |
| `auto_normalize_brand` | Check | Apply Brand Mapping automatically |
| `inspection_type_inventory` | Data | Label for inventory inspections |
| `inspection_type_repair` | Data | Label for repair inspections |
| `supplier_code_prefix` | Data | Supplier code prefix for Items |
| `intake_naming_series` | Data | e.g. `INV-.#####` |
| `intake_id_pattern` | Data | e.g. `CI-.{YYYY}.-.#####` |
| `brand_mapping_rules` | Table (Brand Mapping Rule) | Inline mapping rules |
| `auto_create_consent_form` | Check | Enable automated consent form creation |
| `default_consent_template` | Link (Consent Template) | Template used when automation is enabled |
| `consent_required_for_intake_types` | Select | Which intake types require consent |
| `sla_target_hours` | Int | New. Hours to add when computing the promise-by SLA (default 72). |
| `sla_label` | Data | New. Label displayed with the SLA target (default “Promise by”). |

### 3. Business Logic and Automation

**Python controller:** `clarinet_intake_settings.py`

* `validate()` – ensures referenced records exist, applies fallbacks, and sets
  SLA defaults when omitted.
* `get_intake_settings()` – returns settings as a dict with sane fallbacks and
  surfaces the SLA fields to downstream callers (`create_full_intake`, reports,
  desk widgets).

No custom JavaScript is required; the standard desk form is sufficient.

### 4. Relationships and Dependencies

* Links to **Item Group**, **Warehouse**, **Price List**, **UOM**, and
  **Consent Template** doctypes through their respective configuration fields.
* Embeds **Brand Mapping Rule** rows for on-the-fly manufacturer normalisation.
* Consumed by the Clarinet Intake controller, intake accessories logic, and the
  API SLA resolver.

### 5. Critical Files

* `clarinet_intake_settings.json` – schema and permissions.
* `clarinet_intake_settings.py` – controller logic with validation + helpers.
* `README.md` (this file) – operational notes and field glossary.

_Last updated: 2025-10-11_
