# relative path: repair_portal/hooks.py
# date updated: 2025-07-28
# version: 4.1.0
# purpose: App configuration hooks,
# notes: Added doctype_js for Clarinet Intake mode-specific scripts

# doc_events to link child docs -> Repair Order
from repair_portal.repair import utils as _repair_utils  # noqa: F401

export_python_type_annotations = True
app_name = 'repair_portal'
app_title = 'Repair Portal'
app_publisher = 'Dylan Thompson'
app_description = 'Portals for the Repair Portal App'
app_email = 'info@artisanclarinets.com'
app_license = 'mit'

required_apps = ['frappe', 'erpnext']


# fire this before any DDL, patches or fixtures run
before_install = [
    'repair_portal.install.check_setup_complete',
    'repair_portal.install.seed_item_groups_after_migrate',
]

after_install = [
    'repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes',
    'repair_portal.install.seed_all_from_schemas',
    'repair_portal.utils.install.install_consent_artifacts.install_or_update_consent_artifacts',

]

after_migrate = [
    'repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes',
    
    
    # use if update schemas in scripts/hooks/schemas/*
    #   "repair_portal.install.seed_item_groups_after_migrate",
    #   "repair_portal.install.seed_all_from_schemas",
    
    # Ensure Consent Artifacts are installed/updated
    # 'repair_portal.utils.install.ensure_workflow_prereqs.ensure_workflow_prereqs',

    # 'repair_portal.utils.install.install_consent_artifacts.install_or_update_consent_artifacts',
]


doc_events = {
    'Repair Order': {
        'on_submit': 'repair_portal.repair_order.doctype.repair_order.repair_order.RepairOrder.on_submit',
        'on_cancel': 'repair_portal.repair_order.doctype.repair_order.repair_order.RepairOrder.on_cancel',
    },
    'Clarinet Intake': {
        # after_insert will call our new function
        'after_insert': (
            'repair_portal.intake.doctype.clarinet_intake'
            + '.clarinet_intake_timeline.add_timeline_entries'
        )
    },
    'Instrument': {
        'after_insert': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
        'on_update': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
        'on_change': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
    },
    'Instrument Serial Number': {
        'on_update': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
    },
    # Optional handlers if these doctypes exist in your app/site:
    'Instrument Condition Record': {
        'after_insert': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
        'on_update': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
        'on_trash': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
    },
    'Instrument Media': {
        'after_insert': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
        'on_trash': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
    },
    'Instrument Interaction Log': {
        'after_insert': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
        'on_trash': 'repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change',
    },
    # End Optional handlers

    # Begin Repair Order Doc Events
    "Clarinet Intake": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Instrument Inspection": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Service Plan": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Repair Estimate": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Final QA Checklist": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Measurement Session": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Diagnostic Metrics": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Repair Task": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
     "Stock Entry": {
    "after_submit": "repair_portal.repair.hooks_stock_entry.after_submit_stock_entry"
  }
}


# website_route_rules = [
#     {'from_route': '/frontend/<path:app_path>', 'to_route': 'frontend'},
# ]

# --- [BEGIN Repair Portal (Repair workflow) additions] ---



