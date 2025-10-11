## Doctype: Player Profile

### 1. Overview and Purpose

**Player Profile** is a doctype in the **Player Profile** module that manages and tracks related business data.

**Module:** Player Profile
**Type:** Master/Standard Document

**Description:** Fortune-500 production-ready Player Profile for comprehensive musician CRM tracking, preferences, equipment, and service history.

This doctype is used to:
- Store and manage master or reference data
- Provide configuration or lookup information
- Support other business processes in the application

### 2. Fields / Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `naming_series` | Data | Hidden. Default `PLAYER-.####` naming series selector. |
| `player_profile_id` | Data | **Required**, **Unique**, Read-only. Mirrors document name. |
| `player_name` | Data | **Required**. Full legal name of the player. |
| `preferred_name` | Data | Optional friendly name. |
| `date_of_birth` | Date | Used for COPPA enforcement (<13 disables marketing). |
| `primary_email` | Data | **Required**, **Unique**. Primary email address. |
| `primary_phone` | Data | **Required**. Validated against E.164-friendly pattern. |
| `customer` | Link (Customer) | Optional linked ERPNext customer. |
| `newsletter_subscription` | Check | Marketing opt-in flag (synced with Email Group). |
| `targeted_marketing_optin` | Check | Advanced marketing opt-in (auto-disabled for minors). |
| `mailing_address_line1` | Data | Address line 1 (personal data). |
| `mailing_address_line2` | Data | Address line 2 (personal data). |
| `city` | Data | City (personal data). |
| `state` | Data | State/Province (personal data). |
| `postal_code` | Data | Postal/ZIP code (personal data). |
| `country` | Link (Country) | Country reference. |
| `profile_creation_date` | Date | Read-only. Auto-populated creation date. |
| `last_visit_date` | Date | Read-only. Latest Clarinet Intake or Repair Order date. |
| `customer_lifetime_value` | Currency | Read-only. Sum of submitted Sales Invoices linked to profile. |
| `player_level` | Select | **Required**. Skill level taxonomy. |
| `primary_playing_styles` | Small Text | Free-form list of genres/styles. |
| `primary_teacher` | Data | Visible for student levels only (personal data). |
| `affiliation` | Data | School, ensemble, or organization. |
| `communication_preference` | Select | Preferred contact channel. |
| `referral_source` | Data | Acquisition source. |
| `player_equipment_preferences` | Table (Player Equipment Preference) | Child table for equipment preferences. |
| `intonation_notes` | Small Text | Technician-facing tuning notes. |
| `technician_notes` | Small Text | Internal notes for the repair team. |
| `instruments_owned` | Table (Instruments Owned) | Auto-synced inventory owned by the player. |
| `profile_status` | Select | Lifecycle: Draft → Active → Archived. Drives workflow. |
Student (Advanced)
Amateur/Hobbyist
University Student
Professional (Orchestral)
Professional (Jazz/Commercial)
Educator
Collector) | **Required**. Current skill/professional level of the player |

Standard
High/Open) | Preferred key height setting for clarinet |
| `spring_tension_preference` | Select (Light/Fluid
Standard/Firm
Heavy/Resistant) | Preferred spring tension for key action |
| `preferred_pad_type` | Data | Preferred type of clarinet pads (e.g., skin, synthetic, with or without resonators) |
| `g_sharp_a_connection` | Data | Preference for G#/A key connection type |
| `intonation_notes` | Small Text | Notes about tuning preferences, intonation tendencies, or barrel length preferences |
| `technician_notes` | Small Text | Internal notes for technicians about special requirements or observations |
| `instruments_owned` | Table (Instruments Owned) | List of instruments currently owned by this player |
| `last_visit_date` | Date | Date of most recent visit or service interaction |
| ... | ... | *7 more fields* |

### 3. Business Logic and Automation

#### Backend Logic (Python Controller)

The Python controller (`player_profile.py`) implements the following:

**Lifecycle Hooks:**
- **`validate()`**: Validates document data before saving
- **`before_save()`**: Executes logic before the document is saved
- **`before_insert()`**: Runs before a new document is inserted
- **`on_update()`**: Runs after document updates
- **`on_trash()`**: Executes before document deletion

**Custom Methods:**
- `autoname()`: Deterministic naming using PLAYER- series.
- `_sync_instruments_owned()`: Pulls Instrument Profiles owned by the player.
- `_calculate_clv()`: Aggregates submitted Sales Invoices.
- `_update_last_visit_date()`: Tracks last Clarinet Intake/Repair Order.

**Whitelisted APIs:**
- `get(player_email=None)`: Fetch profile by email with permission checks.
- `save(doc_json)`: Portal-safe update endpoint.
- `get_service_history(player_profile)`: Consolidated intake/repair history.
- `update_marketing_preferences(name, newsletter=None, targeted=None)`: GDPR/COPPA-aware opt-in handler.

#### Frontend Logic (JavaScript)

The JavaScript file (`player_profile.js`) provides:

- **Custom Buttons**: Adds custom action buttons to the form

### 4. Relationships and Dependencies

This doctype has the following relationships:

- Has child table **Player Equipment Preference** stored in the `equipment_preferences` field
- Has child table **Instruments Owned** stored in the `instruments_owned` field
- Links to **Workflow State** doctype via the `workflow_state` field (Workflow State)

### 5. Critical Files Overview

- **`player_profile.json`**: DocType schema definition containing all field configurations, permissions, and settings
- **`player_profile.py`**: Python controller implementing business logic, validations, and lifecycle hooks
- **`player_profile.js`**: Client-side script for form behavior, custom buttons, and UI interactions
- **`test_player_profile.py`**: Unit tests for validating doctype functionality

---

*Last updated: 2025-10-04*
