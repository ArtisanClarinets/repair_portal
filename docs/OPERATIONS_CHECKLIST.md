# Operations Checklist

## Daily
- Run `bench --site <site> migrate` to ensure patches (including `repair_portal.core.patches.*`) are applied.
- Execute `python repair_portal/core/codebase_map.py` to refresh `.build/cross_module_map.json` if any schema or
  hook changes shipped in the last deploy.
- Review structured logs for anomalies:
  - `repair_portal.sla`
  - `repair_portal.inventory`
  - `repair_portal.billing`
  - `repair_portal.notify`
  - `repair_portal.warranty`
  - `repair_portal.tools`
- Verify the Ops Dashboard workspace shows green KPIs for SLA, QA and Billing.

## Weekly
- Audit `Repair Material Movement` entries against stock ledgers to confirm SSOT alignment.
- Run the SLA compliance report and confirm at-risk/breached counts trigger the expected notifications.
- Validate rate-limited endpoints by reviewing Redis key counts for `rl::` prefixes.
- Regenerate the cross-link documentation in `docs/CROSS_LINK_MATRIX.md` after major module work.

## Monthly
- Review user role assignments to ensure only the roles defined in `repair_portal.core.registry.Role` are
  granted elevated permissions.
- Trigger the `repair_portal.core.patches.p003_merge_shadow_models` patch in a staging environment to confirm
  no new legacy records accumulate.
- Execute `bench --site <site> run-tests --module repair_portal` to confirm end-to-end coverage.

## Incident Response
- Use the registry constants in `repair_portal.core.registry` when creating ad-hoc scripts; this guarantees
  consistent queue/event names.
- Leverage `repair_portal.core.services.*` functions inside bench consoles for safe, validated operations.
- Re-run `repair_portal/core/patches/p004_backfill_links_and_visibility.py` if cross-module links drift.

## References
- [Architecture Services](ARCHITECTURE_SERVICES.md)
- [Cross Module Map](CROSS_MODULE_MAP.md)
- [Cross Link Matrix](CROSS_LINK_MATRIX.md)
