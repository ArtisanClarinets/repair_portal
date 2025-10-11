# Player Profile Module

The **Player Profile** module centralizes musician identity, preferences, and lifecycle analytics across the repair_portal app. It links ERPNext Customers, Instrument Profiles, Clarinet Intake records, Repair Orders, and Sales Invoices to present a single source of truth for every player.

## Highlights

- **Lifecycle management** — Draft → Active → Archived workflow with button-driven transitions and archived-state guard rails.
- **Deep integrations** — Automatic linkage with Customers, Instrument Profiles (`owner_player`), Clarinet Intake, Repair Orders, and Sales Invoices (CLV field).
- **Marketing compliance** — COPPA-aware marketing toggles, newsletter sync via configurable Email Group, and GDPR-friendly anonymization guidance.
- **Portal self-service** — Controlled update API that lets verified players maintain contact details without exposing sensitive fields.
- **Operational telemetry** — Customer lifetime value, last visit rollup, and service history aggregation for Clarinet Intake and Repair Orders.

---

## Schema Overview

### Player Profile (`player_profile`)

| Field | Type | Notes |
| --- | --- | --- |
| `player_profile_id` | Data (read-only) | Autoname (`PLAYER-.####`) synced with `name`.
| `player_name` | Data (required, personal data) | Legal name.
| `preferred_name` | Data (personal data) | Used for communications.
| `primary_email` | Data (required, unique, personal data) | Validated email; drives portal identity.
| `primary_phone` | Data (required, personal data) | Regex validated (`^[0-9+()\-\s]{7,20}$`).
| `customer` | Link → Customer | Optional but recommended for billing and permissions.
| `player_level` | Select (required) | Student/Amateur/Professional tiers.
| `profile_status` | Select | Draft / Active / Archived (workflow state).
| `newsletter_subscription` | Check | Player opt-in. Disabled automatically for COPPA (<13).
| `targeted_marketing_optin` | Check | Secondary marketing flag with COPPA enforcement.
| `date_of_birth` | Date | Enables COPPA logic.
| Address fields | Data / Link | Mailing address (GDPR tagged).
| `profile_creation_date` | Date (read-only) | Auto-set on insert.
| `last_visit_date` | Date (read-only) | Derived from latest Clarinet Intake or Repair Order.
| `customer_lifetime_value` | Currency (read-only) | Sum of submitted Sales Invoices linked via custom field `player_profile`.

**Child tables**

- `player_equipment_preferences` → **Player Equipment Preference** (mouthpiece, ligature, reed, instrument link).
- `instruments_owned` → **Instruments Owned** (instrument profile, instrument, serial, model, customer).

**Tracking flags**: `track_changes`, `track_seen`, and `track_views` are enabled for full auditability.

### Player Equipment Preference (Child)

Captures preferred gear per player. Validates linked Instrument Profile entries when set.

### Instruments Owned (Child)

Read-only table synchronized from Instrument Profiles where `owner_player` matches the Player Profile. Includes enforced `customer` linkage for each row.

### Player Profile Settings (Single)

Configures the newsletter Email Group used when syncing marketing subscriptions. Located at **Player Profile Settings** and defaults to “Player Newsletter”.

### Customizations

- **Sales Invoice** now includes a `player_profile` custom Link field (fixture + patch) with an index for performant CLV queries.
- **Instrument Profile** exposes `owner_player` for ownership attribution and filtering.
- **Repair Order** adds `player_profile` (auto-synced from Clarinet Intake / Instrument Profile and pushed to Sales Invoices).
- **Clarinet Intake** surfaces a read-only `player_profile` field which is populated/created automatically during validation.

---

## Server Logic Summary (`player_profile.py`)

| Hook | Key Behaviors |
| --- | --- |
| `autoname` | Generates `PLAYER-.####` identifier and mirrors to `player_profile_id`. |
| `before_insert` | Validates required fields, email, phone, duplicate email, customer existence; sets creation date. |
| `validate` | Re-applies core validation, ensures customer alignment, validates child tables, enforces archived read-only guard, and applies COPPA rules (disables marketing + timeline comment). |
| `before_save` | Syncs owned instruments from Instrument Profiles, recalculates CLV via Query Builder aggregate, and refreshes `last_visit_date` from Clarinet Intake / Repair Order activity. |
| `on_update` | Syncs newsletter membership using configurable Email Group, logs status changes. |
| `on_trash` | Removes newsletter membership, clears Instrument Profile `owner_player`, and deletes Contact links. |

**Marketing Compliance**

- COPPA: Players younger than 13 automatically lose newsletter/targeted opt-ins, newsletter membership is removed, and a timeline comment is recorded.
- GDPR: Personal data fields are tagged. `PlayerProfile.sync_contact()` provides an optional utility to create/update a Contact linked to both the Customer and Player Profile for sites that rely on Contacts. Use Frappe’s Data Deletion Request workflow or redact fields via a small admin method for anonymization.

**Portal APIs**

- `get(player_email=None)` — Returns profile data for staff or the authenticated portal user (matching `primary_email`).
- `save(doc_json)` — Staff have full write access. Portal users may update only whitelisted contact and consent fields after identity verification; writes run through the standard controller validation.
- `get_service_history(player_profile)` — Returns combined Clarinet Intake + Repair Order events (date, type, reference, serial, description) sorted descending.
- `update_marketing_preferences(name, newsletter=None, targeted=None)` — Staff-only helper that re-runs COPPA enforcement.
- `sync_contact(name, force=0)` — Staff utility to ensure a Contact exists with dynamic links to Customer and Player Profile.

All APIs rely on `_ensure_profile_permission` to guard scope and log permission issues.

---

## Client Experience (`player_profile.js`)

- Student-specific fields (`primary_teacher`, `affiliation`) toggle based on `player_level` prefix.
- Inline validation for email/phone with immediate feedback.
- Custom buttons for workflow transitions (Activate, Archive, Restore) using `frappe.model.workflow.apply_workflow`.
- CRM actions: “Email Player”, “Call Player”, “Show Owned Instruments”, and “View Service History” (renders sanitized table via whitelisted method).
- Dashboard comments display Profile Status, Customer Lifetime Value, Last Visit Date, and Profile Age.
- Archived profiles auto-disable fields (except workflow buttons) to preserve history.

---

## Integrations

- **Customer** — `player_profile.customer` scopes reports and portal permissions; Clarinet Intake auto-links profiles to the same Customer and `sync_contact` can create a Contact under that Customer.
- **Instrument Profile** — `owner_player` mirrors Player Profile ownership. `on_trash` clears the link, and Clarinet Intake automatically sets `owner_player` when instruments are created or linked.
- **Clarinet Intake** — Validation finds or creates Player Profiles by email/customer and stores the link. `last_visit_date` queries the most recent intake date.
- **Repair Order** — `player_profile` field auto-populates from linked intake/instrument profile. Sales Invoices generated from Repair Orders inherit the `player_profile` custom field.
- **Sales Invoice** — Custom field `player_profile` plus index ensures CLV calculations stay performant even at scale.
- **Email Group** — Default “Player Newsletter” (configurable). COPPA disables membership automatically.

---

## Portal Self-Service

1. Assign portal users (Customer role) whose login email matches `primary_email`.
2. `player_profile.get()` leverages the session to return the correct record.
3. `player_profile.save(doc_json)` accepts only the allow-listed fields (preferred name, contact details, marketing toggles) and runs full server validation.
4. Attempts to edit restricted fields raise `frappe.PermissionError`.

---

## COPPA & GDPR Guidance

- Set `date_of_birth` for minors to trigger automatic marketing lockouts.
- Use `Player Profile Settings` to select the appropriate newsletter Email Group; the controller creates the default group if missing.
- To anonymize a record, either submit a Data Deletion Request or write a short admin script that clears personal fields and calls `sync_contact` to update downstream contacts.
- Audit logs: Status changes and COPPA actions add timeline comments; `track_changes` surfaces field history.

---

## Administration & Operations

### Initial Setup

1. Install fixtures via `bench migrate` (ensures naming series, email group, and Sales Invoice custom field).
2. Configure **Player Profile Settings** to point to your marketing Email Group (defaults to *Player Newsletter*).
3. Verify the Sales Invoice custom field `player_profile` exists (`Customize Form → Sales Invoice`).
4. Confirm the Repair Order DocType includes the `player_profile` link (already bundled).

### Post-Deploy Checklist

- `bench --site <yoursite> migrate`
- `bench --site <yoursite> clear-cache && bench build`
- `bench --site <yoursite> run-tests --module repair_portal --doctype "Player Profile"`
- Create a sample Player Profile and run workflow transitions (Draft → Active → Archived).
- Submit Clarinet Intake + Repair Order to ensure player linkage and last-visit metrics populate.
- Verify newsletter sync (check Email Group membership) and Sales Invoice CLV rollups.

### Ongoing Operations

- Review `frappe.log_error` for `PlayerProfile` channel weekly.
- Monitor Sales Invoice index health (`SHOW INDEX FROM tabSales Invoice`) if dataset grows rapidly.
- Periodically run `player_profile.sync_contact` for profiles lacking Contacts when CRM modules rely on ERPNext’s Contact doctype.

---

## Tests

Automated tests live under `repair_portal/repair_portal/player_profile/tests/`:

- `test_player_profile_validation.py`
- `test_player_profile_coppa.py`
- `test_player_profile_workflow.py`
- `test_player_profile_instrument_sync.py`
- `test_player_profile_service_history.py`
- `test_player_profile_clv.py`
- `test_player_profile_api_permissions.py`

Run via `bench --site <site> run-tests --module repair_portal --doctype "Player Profile"`.

---

## Troubleshooting

| Symptom | Steps |
| --- | --- |
| Newsletter sync fails | Confirm **Player Profile Settings → Newsletter Email Group** exists; re-save to refresh cache. |
| CLV remains zero | Ensure Sales Invoices use the `player_profile` custom field and are submitted. Run the index patch (`bench execute repair_portal.patches.v15_08_add_player_profile_indexes.execute`). |
| Instrument ownership missing | Confirm Instrument Profile has `owner_player` column (part of module) and that Clarinet Intake successfully linked the player. Use `profile._sync_instruments_owned()` in console to rebuild. |
| Portal user cannot edit profile | Verify the user’s email matches `primary_email` and they possess the `Customer` role only. |

---

## Related Files

- `player_profile.py` — Core controller logic and whitelisted APIs.
- `player_profile.js` — Desk client behavior and dashboards.
- `player_profile_workflow.json` — Unified workflow definition.
- `player_profile_settings.json` — Marketing configuration (Single DocType).
- `v15_08_add_player_profile_indexes.py` — Patch for indexes and Sales Invoice custom field.
- `sales_invoice_custom_fields.json` — Fixture for the Sales Invoice custom field.

The module is ready for Fortune-500 deployments with explicit integrations, compliance guards, and automated tests.
