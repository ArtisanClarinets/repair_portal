# Clarinet Estimator

The clarinet estimator provides a customer-facing workflow for building structured repair estimates from an interactive pad map. It connects diagram selections to pricing rules, composes a `Repair Estimate`, and persists an immutable `Clarinet Pad Map Artifact` with photos for downstream QA.

## Data Model

| Artifact | Purpose | Key Fields |
| --- | --- | --- |
| `Clarinet Estimator Pricing Rule` | Maps a diagram region to parts, labor presets, and multipliers per instrument family. | `instrument_family`, `region_id`, `component_type`, `part_item`, `labor_hours`, `family_multiplier`, `rush_multiplier`, `eta_days` |
| `Clarinet Pad Map Artifact` | Stores the rendered estimate, required photos, and region-level totals. | `instrument_family`, `instrument_serial`, `condition_score`, `eta_days`, `estimated_total`, `photos`, `selections` |
| `Pad Map Artifact Selection` | Child table recording the part and labor breakdown per selected region. | `region_id`, `component_type`, `part_quantity`, `labor_hours`, `line_total` |
| `Pad Map Artifact Photo` | Child table referencing uploaded inspection images. | `file`, `caption` |
| `Repair Estimate` | Updated to store instrument context, rush flag, and estimator notes. | `instrument_family`, `instrument_serial`, `condition_score`, `rush_service`, `pad_map_artifact`, `line_items` |
| `Estimate Line Item` | Enriched child table providing role-aware amounts. | `region_id`, `component_type`, `line_role`, `quantity`, `hours`, `amount` |

## Pricing Rules

* One rule represents a single component (pad, mechanism, cork) of a diagram region.
* Parts pricing uses `Item.standard_rate` (falling back to purchase/valuation rates if needed).
* Labor pricing multiplies `labor_rate × family_multiplier` and applies `rush_multiplier` when the customer requests expedited service.
* `eta_days` is aggregated across selected regions; rush service reduces turnaround by two days without dropping below two days.
* Fixtures ship with baseline B♭ and Bass clarinet rules in `repair_portal/fixtures/clarinet_estimator_pricing_rule.json`. Update via `bench --site $SITE execute repair_portal.tools.estimator_rules.sync` (see Runbook) after editing the fixture.

## Portal Flow

1. Customers navigate to `/clarinet_estimator`. The page auto-detects the instrument family and loads rules via `repair_portal.api.estimator.get_bootstrap`.
2. Diagram buttons toggle `region_id` selections with full keyboard support and ARIA feedback.
3. Client-side rendering previews parts/labor totals using the pricing rules (including rush multipliers).
4. Submission posts a CSRF-protected `FormData` payload (including uploaded photos) to `repair_portal.api.estimator.submit`.
5. `process_estimate_submission` validates ownership, applies pricing, creates or updates a `Repair Estimate`, and persists a linked `Clarinet Pad Map Artifact` with selections and photo attachments.
6. The response returns estimate identifiers, totals, and line-item details so the UI can confirm success.

## Extending the Estimator

* Add new diagram regions by updating the portal template hotspots and creating matching pricing rules (`region_id` must be consistent).
* To support additional instrument families, populate rules for the new family and update `INSTRUMENT_FAMILIES` in `repair_portal/service_planning/clarinet_estimator.py`.
* Pricing automation can be scripted by inserting `Clarinet Estimator Pricing Rule` documents—tests rely on `family_multiplier`, `rush_multiplier`, and `eta_days` being present.
* The estimator reuses existing `Clarinet Pad Map Artifact` records when re-submitted for the same customer and instrument serial, and enforces at least one photo across submissions.

## Error Handling & Safeguards

* Customer access is validated through `ensure_customer_access`; internal roles retain full access.
* Missing pricing rules or item rates raise a `frappe.ValidationError` with actionable messages.
* Serial number, condition score, and photo attachment requirements are enforced server-side and client-side.
* Artifact creation temporarily bypasses mandatory validation to allow file attachments, followed by a full validation save to guarantee photos and selections exist.
