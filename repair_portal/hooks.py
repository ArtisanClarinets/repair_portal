# relative path: repair_portal/hooks.py
# date updated: 2025-07-18
# version: 1.1.0
# purpose: App configuration hooks and fixtures declaration (Updated for Intake JS split)
# notes: Added doctype_js for Clarinet Intake mode-specific scripts

export_python_type_annotations = True
app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "DT"
app_description = "Portals for the Repair Portal App"
app_email = "DT@DT.com"
app_license = "mit"
app_version = "1.2.2"


app_include_js = [
    "/public/js/tone_processor.js",
]

after_install = [
    "repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes",
]
after_migrate = ["repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes"]

doc_events = {
    "Repair Order": {
        "on_submit": "repair_portal.repair_order.doctype.repair_order.repair_order.RepairOrder.on_submit",
        "on_cancel": "repair_portal.repair_order.doctype.repair_order.repair_order.RepairOrder.on_cancel",
    }
}


