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
app_version = "1.2.1"


app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "Your Company"
app_description = "Repair management system"
app_icon = "octicon octicon-tools"
app_color = "blue"
app_email = "support@example.com"
app_license = "MIT"


app_include_js = [
    "/public/js/client_portal/client_portal.bundle.js",
    "/public/js/intake_dashboard/intake_dashboard.bundle.js",
    "/public/js/technician/technician.bundle.js",
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
