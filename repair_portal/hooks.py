# relative path: repair_portal/hooks.py
# date updated: 2025-07-28
# version: 4.1.0
# purpose: App configuration hooks,
# notes: Added doctype_js for Clarinet Intake mode-specific scripts

export_python_type_annotations = True
app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "DT"
app_description = "Portals for the Repair Portal App"
app_email = "DT@DT.com"
app_license = "mit"
app_version = "1.2.2"

required_apps = [
    "frappe",
    "erpnext"
]


# fire this before any DDL, patches or fixtures run
before_install = [ "repair_portal.install.check_setup_complete",
]

after_install = [
    "repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes",
    "repair_portal.install.seed_all_from_schemas",
]

after_migrate = [
	"repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes",
#        "repair_portal.install.seed_item_groups_after_migrate",
        "repair_portal.install.seed_all_from_schemas",
    ]


doc_events = {
    "Repair Order": {
        "on_submit": "repair_portal.repair_order.doctype.repair_order.repair_order.RepairOrder.on_submit",
        "on_cancel": "repair_portal.repair_order.doctype.repair_order.repair_order.RepairOrder.on_cancel",
    },
    "Clarinet Intake": {
        # after_insert will call our new function
        "after_insert": (
            "repair_portal.intake.doctype.clarinet_intake"
            + ".clarinet_intake_timeline.add_timeline_entries"
        )
    }
}


# website_route_rules = [
#     {'from_route': '/frontend/<path:app_path>', 'to_route': 'frontend'},
# ]
