# relative path: repair_portal/hooks.py
# date updated: 2025-07-02
# version: 1.0.1
# purpose: App configuration hooks and fixtures declaration
# notes: Added fixture export for Technician page

app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "DT"
app_description = "Portals for the Repair Portal App"
app_email = "DT@DT.com"
app_license = "mit"
app_version = "1.2.2"


app_include_css = [
         "/public/css/clarinetfest.css",
         "/public/css/product_catalog.css",
        "/assets/repair_portal/dashboard.bundle.css",
]


app_include_js = [
    "/public/js/client_portal/client_portal.bundle.js",
    "/public/js/technician_dashboard/technician_dashboard.bundle.js",
    "/public/js/technician_dashboard/index.dum.js",
    "/public/js/recording_analyzer.bundle.js",
    "/public/js/intonation_recorder.bundle.js",
    "/assets/repair_portal/dashboard.bundle.js",
]

fixtures = [
    "Workflow",
    "Workflow State",
    "Workflow Action",
    "Dashboard Chart",
    "Print Format",
    "Report",
    "Web Form",
    "Server Script",
    "Client Script",
    "Dashboard",
    "Notification",
    "Workspace",
    "Page",
    "Role",
    "Role Profile",
    "Number Card",
    {
        "doctype": "Page",
        "filters": [["name", "in", ["technician"]]],
    },
]

# Other hooks remain unchanged


after_install = [
    "repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes",
]
after_migrate = ["repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes"]

doc_events = {
    "Repair Order": {
        "on_submit": "repair_portal.repair_order.doctype.repair_order.repair_order.RepairOrder.on_submit",
        "on_cancel": "repair_portal.repair_order.doctype.repair_order.repair_order.RepairOrder.on_cancel"
    }
}

portal_menu_items = [
    {
        "title": "My Dashboard",
        "route": "/me/dashboard",
        "reference_doctype": "Client Profile",
        "role": "Customer",
    }
]


