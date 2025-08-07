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


doctype_js = {
    "Import Mapping Setting": {
			"/public/js/import_mapping_setting_autofill.js"
}
	
}

app_include_js = [
    "/repair_portal/repair_portal_settings/doctype/import_mapping_setting/import_mapping_setting.js",
    "/repair_portal/repair_portal_settings/doctype/import_mapping_setting_field/import_mapping_setting_field.js"
]

# fire this before any DDL, patches or fixtures run
before_install = [ "repair_portal.install.check_setup_complete"
]

after_install = [
    "repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes",
"repair_portal.instrument_setup.hooks.load_templates.load_setup_templates",
]
after_migrate = [
   "repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes"
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

fixtures = [
    {
        "dt": "Setup Template",
        "filters": [
            ["template_name", "=", "Bb Clarinet Standard Setup"]
        ]
    }
]


# website_route_rules = [
#     {'from_route': '/frontend/<path:app_path>', 'to_route': 'frontend'},
# ]
