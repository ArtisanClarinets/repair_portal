# Loaner Return Check (`loaner_return_check`)

## Purpose
The Loaner Return Check DocType records the inspection of a loaner instrument when it is returned by a customer. It ensures that return condition, photos, and notes are documented and helps enforce accountability for damages.

## Schema Summary
- **DocType Type:** Standard (not Single, not Child)
- **Key Fields:**
  - `linked_loaner` (Link → Loaner Instrument, Required): Reference to the issued loaner
  - `condition_notes` (Text): Notes about condition upon return
  - `return_photos` (Attach Image): Photos documenting return state
  - `damage_found` (Check): Whether damage was observed
  - `return_date` (Date): When instrument was returned
  - `workflow_state` (Link → Workflow State, Read Only): Tracks workflow stage

## Business Rules
- Each return check must be linked to an existing Loaner Instrument.
- If `damage_found` is checked, `condition_notes` must be provided.
- Photos can be attached to strengthen documentation and accountability.
- Workflow integration allows for escalation (e.g., Damage Review).

## Python Controller Logic
File: `loaner_return_check.py`

- **Class:** `LoanerReturnCheck(Document)`
- **Methods:**
  - `validate()`: Ensures notes are included if damage is flagged.

### Example Logic
```python
if self.damage_found and not self.condition_notes:
    frappe.throw("Please include condition notes when damage is flagged.")
```

## Client-Side Script
- None currently.
- Possible enhancements:
  - Auto-prompt to attach photos if `damage_found` is checked.
  - Dashboard status indicator when return check is pending.

## Integration Points
- **Loaner Instrument**: Linked via `linked_loaner`
- **Workflow**: Uses `workflow_state` for tracking return process
- **Customer**: Permissions allow owner-submitted return confirmations

## Validation Standards
- `linked_loaner`: Required
- `damage_found`: Requires condition notes
- `return_date`: Recommended to be provided at time of return

## Usage Examples
- **Normal Return:**  
  `linked_loaner: LN-2025-001, damage_found: 0, condition_notes: "No issues observed", return_date: 2025-08-16`
- **Damaged Return:**  
  `linked_loaner: LN-2025-002, damage_found: 1, condition_notes: "Crack in lower joint", return_photos: attached`

## Changelog
- **2025-08-16**: Documentation created.
- **2025-06-12**: Validation logic requiring notes when damage flagged was added.

## Dependencies
- **Frappe Framework**
- **Loaner Instrument (linked doctype)**
- **Workflow State (for workflow tracking)**