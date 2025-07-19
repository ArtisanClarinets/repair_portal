## 2025-07-18
- Split Clarinet Intake controller and desk scripts: now cleanly separated for Inventory vs Repair.
- Added `item_code` field (required for Inventory only) and updated doctype schema.
- Inventory intake now auto-creates ERPNext Serial No, Initial Intake Inspection, and Clarinet Initial Setup.
- Added `clarinet_intake_inventory.py` and `clarinet_intake_repair.py` for business logic separation.
- JS logic split into `clarinet_intake_inventory.js` and `clarinet_intake_repair.js` and loaded via hooks.py `doctype_js`.
- Robust error logging and required field enforcement on both backend and frontend.
- Added automated test for inventory intake automation.
- README.md in doctype/clarinet_intake fully explains roadmap, code, and onboarding for new devs.
