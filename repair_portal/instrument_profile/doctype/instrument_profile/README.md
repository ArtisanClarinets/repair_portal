# Instrument Profile — Materialized Snapshot

**Goal:** Make `Instrument Profile` a single, reliable “snapshot” of an instrument.  
It synchronizes canonical identity fields from related doctypes and exposes an API that returns
a full aggregated view (owner, serial record, accessories, media, condition history, interactions).

---

## How it works

### 1) Service Layer
File: `repair_portal/instrument_profile/services/profile_sync.py`

- `sync_now(profile=None, instrument=None)`  
  Ensures the profile exists and updates scalar fields on `Instrument Profile` from canonical sources.

- `get_snapshot(instrument=None, profile=None)`  
  Returns a **full aggregated dictionary** including:
  - `instrument` (selected fields from Instrument, discovered from live schema)
  - `owner` (Customer)
  - `serial_record` (Instrument Serial Number)
  - `accessories` (list) — if `Instrument Accessory` exists
  - `media` (list) — if `Instrument Media` exists
  - `conditions` (list) — if `Instrument Condition Record` exists
  - `interactions` (list) — if `Instrument Interaction Log` exists
  - `headline` and `profile_name`

> **Schema-safe selectors**: The service inspects DocType metadata to only select columns that actually exist on your site.  
> Ordering also auto-falls back to `creation desc` if a preferred order field isn’t present.  
> This eliminates SQL errors like `Unknown column 'accessory_type' in 'SELECT'`.

### 2) Controller
File: `repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py`

- Treats key identity/ownership fields as **read-only** (managed by the service).
- Triggers a sync on insert/update (with guards to avoid loops).

### 3) Client (Form UI)
File: `repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.js`

- Adds a **“Sync Now”** button on the Profile form.
- Shows warranty/status indicators on the dashboard.

### 4) Hooks for Auto-Sync
Add this block (merge with your `doc_events`) in `repair_portal/hooks.py`:

```python
doc_events = globals().get("doc_events", {}) or {}

doc_events.update({
    "Instrument": {
        "after_insert": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_update": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_change": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
    },
    "Instrument Serial Number": {
        "on_update": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
    },
    # Optional if present in your site:
    "Instrument Condition Record": {
        "after_insert": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_update": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_trash": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
    },
    "Instrument Media": {
        "after_insert": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_trash": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
    },
    "Instrument Interaction Log": {
        "after_insert": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_trash": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
    },
})
