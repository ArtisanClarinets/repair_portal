# Intake API Surface (v3)

This document describes the Fortune-500 hardened API surface implemented in
`repair_portal/intake/api.py`. All endpoints are **desk-only** with
`allow_guest=False`, rate limiting, idempotency (where applicable), and structured
telemetry to the `intake_ui_audit` and `intake_ui_security` loggers.

## Security & Role Requirements

* **Allowed roles:** `System Manager`, `Repair Manager`, `Intake Coordinator`.
  A caller must hold at least one of the roles. The API also honours standard
  DocType permissions for any linked records.
* **Rate limiting:** enforced per user via Redis using a token bucket pattern
  (see individual limits below). Exceeding limits raises
  `frappe.TooManyRequestsError`.
* **Idempotency:** state-changing endpoints compute an idempotency key using the
  payload and the current hour (or the provided `session_id`). Results are cached
  for 5 minutes and subsequent identical requests return the cached response.
* **Telemetry:** each call emits a structured log with the schema:

```json
{
  "op": "<endpoint>",
  "status": "ok" | "error",
  "actor": "user@example.com",
  "ip": "127.0.0.1",
  "session_id": "ISN-1234",
  "idempotency_key": "...",
  "request_hash": "sha256-...",
  "timings_ms": {"total": 12, "db": 0},
  "refs": {"intake": "CI-0001", "instrument": "INST-0001"},
  "err": {"code": "ValidationError", "msg": "Sanitised message"}
}
```

PII (emails/phones) is masked inside `refs` and `err` prior to logging.

## Endpoint Reference

### `search_customers(query: str) -> list`

* **Purpose:** typeahead lookup for desk wizard customer selection.
* **Fields returned:** `name`, `customer_name`, `email_id`, `mobile_no`.
* **Rate limit:** 120 requests / 60 seconds / user.
* **Telemetry:** `op="search_customers"`, `refs={"matches": <count>}`.

### `search_instruments(q: dict) -> list`

* **Inputs:** optional keys `serial`, `brand`, `model`.
* **Behaviour:** normalises serial numbers via `utils.serials.normalize_serial`
  and searches `Instrument` by serial/brand/model.
* **Rate limit:** 120 / 60s / user.
* **Telemetry:** `refs={"matches": <count>}`.

### `upsert_customer(payload: dict) -> {customer, contact, address}`

* **Delegates to** `intake.services.intake_sync.upsert_customer` for the heavy
  lifting, then resolves linked Contact and Address (idempotent by email/phone).
* **Required fields:** `customer_name`, `email` (or `email_id`), `phone`.
* **Rate limit:** 60 / 60s / user.
* **Telemetry:** logs customer link on success; failures are routed to
  `intake_ui_security` when permission-related.

### `upsert_player_profile(payload: dict) -> {player_profile}`

* **Purpose:** idempotent Player Profile maintenance keyed by primary email or
  phone. Required fields: `player_name`, `primary_email`.
* **Default player level:** `Amateur/Hobbyist` if omitted.
* **Rate limit:** 60 / 60s / user.

### `create_full_intake(payload: dict) -> {intake, instrument, profile?, inspection?, loaner?}`

* **Responsibilities:**
  1. Validates caller roles and rate limits (30 / 60s / user).
  2. Upserts the customer (and optional player profile).
  3. Finds or creates the Instrument using `utils.serials` helpers and brand
     mapping.
  4. Builds a `Clarinet Intake`, applying service notes and accessories, then
     inserts + submits the document to trigger the controller’s automation
     (inspection, ISN linking, etc.).
  5. Computes SLA via `resolve_sla` and sets `promised_completion_date`.
  6. Optionally links a selected `Loaner Instrument` by writing its `intake`
     field (no checkout state change).
  7. On success, caches the result for idempotency and transitions the related
     `Intake Session` (if provided) to `Submitted`.
* **Error handling:** wraps execution in a savepoint, logs sanitized failures,
  and marks the session as `Abandoned` with an `error_trace` snapshot.

### `loaner_prepare(payload: dict) -> {loaner}`

* **Purpose:** validates that a loaner instrument (`Loaner Instrument`) is
  available (status in Draft/Returned/Available) before the wizard continues.
* **Rate limit:** 30 / 60s / user.
* **Telemetry:** success logs include the loaner name and status; unavailable
  loaners raise `frappe.ValidationError` and log to `intake_ui_security`.

### `resolve_sla(intake_payload: dict | None) -> {target_dt, label}`

* **Reads** the Single DocType **Clarinet Intake Settings** (fields
  `sla_target_hours`, `sla_label`).
* **Fallbacks:** defaults to 72 hours / “Promise by” when unset.
* **Usage:** called internally by `create_full_intake`; exported for reporting
  or desk UI badges.

## SLA Configuration

The Single DocType `Clarinet Intake Settings` (now located at
`repair_portal/repair_portal/doctype/clarinet_intake_settings/`) exposes:

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `sla_target_hours` | Int | 72 | Number of hours after submission used to compute `target_dt`. |
| `sla_label` | Data | Promise by | Label displayed alongside the SLA target. |

Updating these values immediately affects new `create_full_intake` requests and
calls to `resolve_sla`.

## Logging & Observability

All endpoints emit to:

* `intake_ui_audit` – success paths, operational metrics.
* `intake_ui_security` – permission errors, rate-limit violations, validation
  failures tied to misuse.

Each log entry includes masked PII, the computed `request_hash`, timings, and
relevant document references (`refs`). This structure is designed for ingestion
into SIEM tooling and supports filtering by operation, status, or actor.

## Testing Hooks

Python tests covering this module live under `repair_portal/intake/`:

* `test_intake_api_create_full_intake.py`
* `test_upsert_customer_and_player_profile.py`
* `test_loaner_flow.py`
* `test_sla_resolver.py`

A fixture `repair_portal/repair_portal/fixtures/test_seed.json` seeds baseline
Brands, Customers, Loaner Instruments, and a Consent Template for deterministic
results.
