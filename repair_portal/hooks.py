from . import __version__ as app_version

app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "DT"
app_description = "Clarinet focused clarinet repair portal"
app_email = "info@artisanclarinets.com"
app_license = "MIT"

# Fixtures to keep certain customizations portable
fixtures = [
    "Custom Field",
    "Property Setter",
    {"dt": "Workspace", "filters": [["name", "in", [
        "Repair Portal",
        "Intake",
        "Inspection",
        "Service Planning",
        "Repair Logging",
        "QA",
        "Tools"
    ]]]},
    "Client Script",
    "Server Script",
    "Custom DocPerm",
    "Translation"
]

# Document Events
# ----------------
doc_events = {}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [],
    "weekly": [],
    "monthly": [],
    "hourly": [],
    "all": []
}
