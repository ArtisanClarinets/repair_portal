# Clarinet Intake Settings (`clarinet_intake_settings`)

## Purpose
The Clarinet Intake Settings DocType provides centralized configuration for all Clarinet Intake workflows. It defines default warehouses, item groups, pricing, naming series, and automation behaviors used when instruments are processed.

## Schema Summary
- **DocType Type:** Single (issingle = 1)
- **Key Sections:**
  - **Defaults:**
    - `default_item_group`: Default Item Group for intake-created items (default: "Clarinets")
    - `default_inspection_warehouse`: Warehouse used for inspections
    - `buying_price_list`: Price List for procurement (default: "Standard Buying")
    - `selling_price_list`: Price List for sales (default: "Standard Selling")
    - `stock_uom`: Default UOM for stock entries (default: "Nos")
  - **Automation & Behavior:**
    - `require_inspection`: Enforce creation of inspection on intake (default: enabled)
    - `auto_create_initial_setup`: Automatically generate Clarinet Initial Setup for new inventory
    - `notify_on_stock_issue`: Notify users when stock problems occur
  - **Labels & Mapping:**
    - `inspection_type_inventory`: Label for inventory inspections (default: "Initial Inspection")
    - `inspection_type_repair`: Label for repair inspections (default: "Arrival Inspection")
    - `supplier_code_prefix`: Optional prefix for supplier coding
    - `intake_naming_series`: Naming series for intake records (default: "INV-.#####")
    - `brand_mapping_rules`: Child table of **Brand Mapping Rule**

## Business Rules
- All intake-related automation reads from this configuration.
- Enforced by controllers in `clarinet_intake.py` and other intake doctypes.
- Any changes take effect immediately across the system.

## Python Controller Logic
File: `clarinet_intake_settings.py`

- **Class:** `ClarinetIntakeSettings(Document)`
  - Minimal controller; inherits core Frappe validation.
- **Utility:**
  ```python
  def get_intake_settings():
      """Returns Clarinet Intake Settings as a dict."""
      return frappe.get_single("Clarinet Intake Settings").as_dict()
  ```
  Used by other doctypes to fetch settings in a single call.

## Client-Side Script
- None (settings are managed directly in the form).

## Integration Points
- **Clarinet Intake**: Uses defaults for warehouse, pricing, and automation.
- **Instrument Inspection**: Driven by `require_inspection` and inspection type fields.
- **Clarinet Initial Setup**: Created automatically if `auto_create_initial_setup` is enabled.
- **Brand Mapping Rule**: Linked table for normalizing brand names.

## Validation Standards
- `default_item_group` must reference an existing Item Group.
- `default_inspection_warehouse` must reference a valid Warehouse.
- Naming series must conform to Frappe format rules.
- Child table `brand_mapping_rules` enforces uniqueness of brand mappings.

## Usage Examples
- **New Inventory Intake:**  
  Automatically applies `default_item_group`, sets warehouse to `default_inspection_warehouse`, and creates Initial Setup if enabled.
- **Repair Intake:**  
  Inspection is auto-created using the `inspection_type_repair` label.

## Changelog
- **2025-08-16**: Documentation created with schema, business rules, and integration details.

## Dependencies
- **Frappe Framework**
- **Brand Mapping Rule (child table)**
- **Clarinet Intake** (consumes settings)
- **Instrument Inspection**
- **Clarinet Initial Setup**