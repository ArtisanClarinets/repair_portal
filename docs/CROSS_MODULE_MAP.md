# Cross Module Map

This document is auto-generated from `repair_portal/core/codebase_map.py`.

## Summary
* Total DocTypes scanned: 97
* Client scripts discovered: 59
* Python controllers discovered: 463
* Registered hooks: 14
* Whitelisted methods: 105

## DocTypes by Module
- Repair: 16
- Repair Logging: 14
- Instrument Setup: 12
- Customer: 10
- Instrument Profile: 10
- Intake: 9
- Service Planning: 5
- Player Profile: 4
- Lab: 3
- Repair Portal Settings: 3
- Enhancements: 2
- Inventory: 2
- QA: 2
- Repair Portal: 2
- Tools: 2
- Inspection: 1

## Link Field Inventory
| DocType | Fieldname | Links To |
| --- | --- | --- |
| Barcode Scan Entry | linked_item | Item |
| Clarinet Initial Setup | amended_from | Clarinet Initial Setup |
| Clarinet Initial Setup | inspection | Instrument Inspection |
| Clarinet Initial Setup | instrument | Instrument |
| Clarinet Initial Setup | instrument_profile | Instrument Profile |
| Clarinet Initial Setup | intake | Clarinet Intake |
| Clarinet Initial Setup | serial | Instrument Serial Number |
| Clarinet Initial Setup | setup_template | Setup Template |
| Clarinet Initial Setup | technician | User |
| Clarinet Intake Settings | buying_price_list | Price List |
| Clarinet Intake Settings | default_consent_template | Consent Template |
| Clarinet Intake Settings | default_inspection_warehouse | Warehouse |
| Clarinet Intake Settings | default_item_group | Item Group |
| Clarinet Intake Settings | selling_price_list | Price List |
| Clarinet Intake Settings | stock_uom | UOM |
| Clarinet Pad Entry | parent_pad | Clarinet Pad Entry |
| Clarinet Pad Map | clarinet_model | Instrument Model |
| Clarinet Pad Map | instrument_category | Instrument Category |
| Clarinet Setup Log | action_by | User |
| Clarinet Setup Log | customer | Customer |
| Clarinet Setup Log | initial_setup | Clarinet Initial Setup |
| Clarinet Setup Log | instrument_profile | Instrument Profile |
| Clarinet Setup Log | serial | Instrument Serial Number |
| Clarinet Setup Task | amended_from | Clarinet Setup Task |
| Clarinet Setup Task | assigned_to | User |
| Clarinet Setup Task | clarinet_initial_setup | Clarinet Initial Setup |
| Clarinet Setup Task | instrument | Instrument |
| Clarinet Setup Task | parent_task | Clarinet Setup Task |
| Clarinet Setup Task | serial | Instrument Serial Number |
| Clarinet Task Depends On | task | Clarinet Setup Task |
| Clarinet Template Task Depends On | subject | Clarinet Template Task |
| Client Instrument Profile | instrument_owner | Customer |
| Client Instrument Profile | ownership_transfer_to | Customer |
| Client Instrument Profile | serial_no | Serial No |
| Consent Autofill Mapping | source_doctype | DocType |
| Consent Form | consent_template | Consent Template |
| Consent Form | customer | Customer |
| Consent Linked Source | source_doctype | DocType |
| Consent Log Entry | reference_doctype | DocType |
| Consent Log Entry | technician | User |
| Customer External Work Log | instrument | Instrument |
| Customer Upgrade Request | amended_from | Customer Upgrade Request |
| Customer Upgrade Request | customer | Customer |
| Customer Upgrade Request | serial | Instrument |
| Diagnostic Metrics | customer | Customer |
| Diagnostic Metrics | instrument_profile | Instrument Profile |
| Diagnostic Metrics | repair_order | Repair Order |
| Estimate Line Item | part_code | Item |
| Final Qa Checklist | customer | Customer |
| Final Qa Checklist | instrument_profile | Instrument Profile |

## Hook Assignments
| Hook | Kind | Value |
| --- | --- | --- |
| export_python_type_annotations | Constant | `True...` |
| app_name | Constant | `'repair_portal'...` |
| app_title | Constant | `'Repair Portal'...` |
| app_publisher | Constant | `'Dylan Thompson'...` |
| app_description | Constant | `'Portals for the Repair Portal App'...` |
| app_email | Constant | `'info@artisanclarinets.com'...` |
| app_license | Constant | `'mit'...` |
| required_apps | List | `['frappe', 'erpnext']...` |
| fixtures | List | `[
    {
        'doctype': 'Role',
        'filters': [["rol...` |
| before_install | List | `[
    'repair_portal.install.check_setup_complete',
    'rep...` |
| after_install | List | `[
    'repair_portal.scripts.hooks.reload_all_doctypes.reloa...` |
| after_migrate | List | `[
    'repair_portal.scripts.hooks.reload_all_doctypes.reloa...` |
| doc_events | Dict | `{
    "Repair Order": {
        "on_submit": "repair_portal....` |
| scheduler_events | Dict | `{
    'daily': [
        'repair_portal.intake.tasks.cleanup...` |