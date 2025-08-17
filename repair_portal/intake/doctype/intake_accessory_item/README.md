# Intake Accessory Item (`intake_accessory_item`)

## Purpose
The Intake Accessory Item DocType records accessories associated with a clarinet intake, such as cases, reeds, mouthpieces, or cleaning kits. It ensures that all items received with an instrument are documented and tracked.

## Schema Summary
- **DocType Type:** Child Table (linked to Clarinet Intake)
- **Naming:** Autoname from `accessory`
- **Key Fields:**
  - `accessory` (Data, Required): Name or description of accessory
  - `quantity` (Int, default = 1): Number of items included
  - `notes` (Small Text): Optional notes or condition comments

## Business Rules
- Accessories are tracked alongside clarinet intake records.
- Each row represents one type of accessory with quantity and notes.
- Zero quantity is allowed but generates a user-facing warning.
- Negative quantities are strictly disallowed.

## Python Controller Logic
File: `intake_accessory_item.py`

- **Class:** `IntakeAccessoryItem(Document)`
- **Methods:**
  - `validate()`: Ensures accessory description is provided and quantity is valid.

### Example Logic
```python
if not self.accessory:
    frappe.throw("Accessory description cannot be empty.")

if self.quantity is None:
    self.quantity = 1

if self.quantity < 0:
    frappe.throw("Quantity cannot be negative.")

if self.quantity == 0:
    frappe.msgprint("Warning: Quantity is set to zero. Consider updating if this is unintended.")
```

## Client-Side Script
- None currently.
- Possible enhancements:
  - Auto-suggest common accessories (e.g., case, mouthpiece).
  - Auto-default notes field with condition templates.

## Integration Points
- **Clarinet Intake:** Parent document, accessories are attached as child records.
- **Inventory Tracking:** Provides context for accessory inclusion during intake.
- **Customer Communication:** Notes may be included in intake reports.

## Validation Standards
- `accessory`: Required, must be descriptive.
- `quantity`: Must be a non-negative integer.
- `notes`: Optional free-text field.

## Usage Examples
- `accessory: Case, quantity: 1`
- `accessory: Reeds, quantity: 10, notes: Vandoren size 3`
- `accessory: Mouthpiece Cap, quantity: 0 (warns user)`

## Changelog
- **2025-08-16**: Initial documentation created.

## Dependencies
- **Frappe Framework**
- **Clarinet Intake (parent doctype)**