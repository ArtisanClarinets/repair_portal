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
| `player_profile_id` | Data | **Required**, **Unique**, Read-only. Default: `New`. Auto-generated unique identifier for this player profile |
| `player_name` | Data | **Required**. Full legal name of the player |
| `preferred_name` | Data | Name the player prefers to be called |
| `primary_email` | Data | **Required**, **Unique**. Primary email address for communication |
| `primary_phone` | Data | Primary phone number |
| `mailing_address` | Small Text | Complete mailing address for correspondence and shipping |
| `profile_creation_date` | Date | Read-only. Default: `Today`. Date when this profile was first created |
| `player_level` | Select (Student (Beginner)
Student (Advanced)
Amateur/Hobbyist
University Student
Professional (Orchestral)
Professional (Jazz/Commercial)
Educator
Collector) | **Required**. Current skill/professional level of the player |
| `primary_playing_styles` | Small Text | Default: `0`. Comma-separated list of playing styles: Orchestral, Chamber, Solo, Jazz, Klezmer, Contemporary, Concert Band |
| `affiliation` | Data | Current musical organization, orchestra, or educational institution |
| `primary_teacher` | Data | Name of primary teacher or mentor |
| `equipment_preferences` | Table (Player Equipment Preference) | Detailed equipment preferences for mouthpiece, ligature, reeds, barrel, etc. |
| `key_height_preference` | Select (Low/Close
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
- `autoname()`: Custom business logic method
- `get_service_history()`: Custom business logic method
- `get_equipment_recommendations()`: Custom business logic method
- `update_marketing_preferences()`: Custom business logic method

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
