# Player Profile Module

## Workflow Consolidation — 2025-07-27

**Major update:**
- Consolidated two overlapping workflow files (`player_profile_workflow.json`, `player_profile_setup.json`) into a single canonical workflow for the `Player Profile` doctype.
- The unified workflow covers the states: Draft → Active → Archived, with all transitions performed by the Repair Manager role only.
- Legacy or non-aligned states such as `Linked to Client` have been removed for clarity and maintainability.
- All forms, reports, and automations now reference only the official workflow states, matching the select field options.

> This change reduces confusion, prevents workflow collisions, and aligns player profile lifecycle with Frappe/ERPNext best practices.

---

For details, see `/workflow/player_profile_workflow/player_profile_workflow.json` and project changelog.