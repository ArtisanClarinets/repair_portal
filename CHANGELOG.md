## [2025-07-27] Player Profile Workflow Consolidation

- Merged and simplified workflows for Player Profile: removed legacy `player_profile_setup.json`, now only `player_profile_workflow.json` is active and default.
- Official workflow states: Draft, Active, Archived. All transitions handled by Repair Manager.
- Improved auditability and reduced potential workflow collisions.
- Updated documentation in player_profile/README.md.

---
