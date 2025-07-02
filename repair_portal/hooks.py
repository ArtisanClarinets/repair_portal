# File: repair_portal/repair_portal/hooks.py
# Date Updated: 2025-06-29
# Version: 1.1
# Purpose: App hooks and asset includes

app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "Your Company"
app_description = "Repair management system"
app_icon = "octicon octicon-tools"
app_color = "blue"
app_email = "support@example.com"
app_license = "MIT"


app_include_js = [
    "/lab/page/intonation_recorder/intonation_recorder.js",
    "/lab/page/impedance_recorder/impedance_recorder.js",
    "/lab/page/lab_dashboard/lab_dashboard.js",
    "/lab/page/leak_test_recorder/leak_test_recorder.js",
    "/lab/page/tone_fitness_recorder/tone_fitness_recorder.js",
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
    "Number Card"]

# Other hooks remain unchanged


after_install = [""
    "repair_portal.qa.setup.clarinet_qc.sync_qc",
    "repair_portal.scripts.reload_all_doctypes.reload_all_doctypes",
]
after_migrate = ["repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes"]

