# Developer Logic Summary — MRW Artisan Clarinets (2025-07-14)

## Overview
This summary documents core automation, entity relationships, and recent changes (2025-07-14) to clarify current portal logic for future developers.

---

## Core Relationships

- **Client Profile**: Links to Customer, may have multiple Player Profiles.
- **Player Profile**: Linked to Client Profile; represents musician or user.
- **Instrument Profile**: Unique instrument record; links to Serial No, Client Profile, and Player Profile. Stores most recent Intake & Setup.
- **Clarinet Intake**: Intake event for each instrument arrival. Links to Instrument Profile and, for inventory, triggers Clarinet Initial Setup.
- **Clarinet Initial Setup**: Setup and QA for new instruments. Linked to Intake and Instrument Profile. Tracked status.
- **Repair Order**: Only created for "Repair" type intakes (not inventory).


## Current Automation (Post-2025-07-14)
- **Inventory Intake Submit**:
  - Creates Instrument Profile (if not linked)
  - Creates Clarinet Initial Setup, links both ways (Intake ⇄ Setup, Setup ⇄ Intake & Instrument)
  - Does *not* create Repair Order
- **Repair Intake Submit**:
  - (Legacy) May trigger Repair Order creation (future dev: see intake_type branching in controller)
- **Validation**:
  - Setup cannot save without Intake and Instrument Profile
  - All error cases logged using `frappe.log_error`
- **Client Script**:
  - Intake desk form: Inventory intakes show “Open Initial Setup” button
  - No Repair Order action for Inventory
- **Test Coverage**:
  - Test cases enforce creation & linkage (see `test_clarinet_intake.py`, `test_inventory_intake_flow.py`, `test_clarinet_initial_setup.py`)


## Quick Visual (Entity Relationships)

```
Client Profile
   └─ Player Profile(s)
        └─ Instrument Profile(s)
             └─ Clarinet Intake(s)
                  └─ Clarinet Initial Setup

(Repair Order)
   └─ Only for Repair intakes, not Inventory
```

## Recent Changes (2025-07-14)
- Unified inventory intake logic around Instrument Setup (not Repair Order)
- Refactored all affected DocTypes, controllers, and tests
- Updated user-facing flows (desk buttons, error handling)

---

For more, see CHANGELOG.md. All core linkage fields now have in-list visibility and docstring explanations.
