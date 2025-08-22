# relative path: repair_portal/hooks.py
# date updated: 2025-07-28
# version: 4.1.0
# purpose: App configuration hooks,
# notes: Added doctype_js for Clarinet Intake mode-specific scripts

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
]

after_migrate = [
    'repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes',
    #   "repair_portal.install.seed_item_groups_after_migrate",
    #   "repair_portal.install.seed_all_from_schemas",
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
}


app_include_css = ['/assets/repair_portal/css/clarinet_editor.css']

# website_route_rules = [
#     {'from_route': '/frontend/<path:app_path>', 'to_route': 'frontend'},
# ]
