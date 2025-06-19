# Web Pages Guide for the Clarinet Repair Portal

## Overview
This directory contains all **Python page controllers** for custom web routes in the Clarinet Repair Portal for ERPNext/Frappe v15.

- All **user-facing web pages** are built using the Frappe standard: each route is backed by a `.py` controller in `/www/`, which passes context to a corresponding Jinja template in `/templates/pages/` (or `/templates/generators/` for generator DocTypes).
- This app is a central hub for clients, technicians, and players to manage and view all aspects of clarinet servicing and ownership.

---

## How Frappe Web Pages Work (v15 Best Practices)

- **Each web page route** (e.g., `/my_instruments`) is created by a Python file in `/www/` (e.g., `my_instruments.py`).
- The controller's `get_context(context)` method loads any necessary data and attaches variables to the context.
- The matching Jinja template (same name, `.html`, in `/templates/pages/`) renders the page using those variables.
- **Do NOT put templates in `/www/`**—keep all templates in `/templates/pages/`.
- **Never use Jinja DB queries in templates** (e.g., `frappe.get_all`). Always supply data from the controller.
- Generator DocTypes (auto-generated detail pages) use templates in `/templates/generators/`.
- All pages extend `templates/web.html` for consistent theming.

---

## Core Portal Concepts

### 1. **Instrument Portal (Central Hub for Instruments)**
- **Instrument Profile** is the primary DocType for each clarinet.
  - See: `../instrument_setup/doctype/instrument_profile/instrument_profile.json`
- Each user sees only their own instruments (filtered by `client_profile` or `owner`).
- Detail view for each instrument: `/instrument_profile?name=INSTRUMENT_NAME`
- All fields, repair logs, status, and notes for the instrument are shown.

### 2. **Client Profile**
- Stores the client/user’s identity and linked user.
  - See: `../instrument_setup/doctype/client_profile/client_profile.json`
- Used to restrict access to instruments and repairs for each user.

### 3. **Player Profile**
- Represents players associated with the client (students, professionals, etc).
  - See: `../instrument_setup/doctype/player_profile/player_profile.json`
- Player profiles are listed on `/player_profiles` and detailed on `/my_players`.

### 4. **Repair Log / Service Summary**
- **Repair Log:** Each repair performed, with fields for instrument, technician, description, etc.
  - See: `../repair_logging/doctype/repair_log/repair_log.json`
- **Clarinet Repair Log:** Used for advanced inspections and pad maps.
  - See: `../repair_logging/doctype/clarinet_repair_log/clarinet_repair_log.json`
- Service summaries and dashboards (technician and client) are based on these logs.

### 5. **Technician Dashboard**
- Technicians see repairs assigned to them via `/technician_dashboard`.
- Uses the `Repair Log` DocType, filtered by `technician` and status.

### 6. **Repair Request and Status Tracking**
- `/repair_request`: Users submit new repair/service orders.
- `/repair_status`: Users can track status and history for a repair (requires Service Order Tracker DocType).
  - See: `../service_planning/doctype/service_order_tracker/service_order_tracker.json`

---

## Directory Map

- `my_instruments.py`         →  Main instrument list view
- `my_repairs.py`             →  Client/user's repair history
- `my_players.py`             →  Player directory (for each client)
- `player_profiles.py`        →  List of player profiles
- `service_summary.py`        →  All services/repairs for client
- `technician_dashboard.py`   →  Technician job dashboard
- `repair_request.py`         →  New repair request page
- `repair_pulse.py`           →  Real-time updates for a repair request
- `repair_status.py`          →  Repair tracking page
- `instrument_profile.py`     →  Instrument detail (dynamic, secure)
- `pad_map.py`                →  Pad map and inspection visuals

---

## Associated Doctypes (Relative Paths)

- **Instrument Profile:** `../instrument_setup/doctype/instrument_profile/instrument_profile.json`
- **Client Profile:** `../instrument_setup/doctype/client_profile/client_profile.json`
- **Player Profile:** `../instrument_setup/doctype/player_profile/player_profile.json`
- **Repair Log:** `../repair_logging/doctype/repair_log/repair_log.json`
- **Clarinet Repair Log:** `../repair_logging/doctype/clarinet_repair_log/clarinet_repair_log.json`
- **Service Order Tracker:** `../service_planning/doctype/service_order_tracker/service_order_tracker.json`

---

## Adding a New Web Page (Example)
1. Create `your_page.py` in this `/www/` directory.
2. Add `get_context(context):` in your controller to load any required data.
3. Create a matching `your_page.html` template in `/templates/pages/`.
4. Route will be `/your_page` in the portal.

---

## Notes
- All portal pages require users to be authenticated unless marked public.
- All business logic, filters, and DB queries must be in the controller.
- Template files use only context variables provided by controllers for security and maintainability.
- All templates must extend `templates/web.html` for a consistent look.

---

For any questions or contributions, see the main project README or contact Dylan Thompson (MRW Artisan Instruments).

### 2024-06-19
- Legacy `repair_portal/repair_portal/www` pages consolidated into this directory.
- Unused pad map templates removed; `repair_pulse.html` moved to `templates/pages/`.

### 2025-07-02
- Controller context updated with JSON dumps and empty messages for list pages.
- Templates aligned with new context variables.
