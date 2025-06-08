from . import __version__ as app_version

app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "MRW Artisan Instruments"
app_description = "Clarinet repair management portal"
app_email = "support@artisanclarinets.com"
app_license = "MIT"

fixtures = [
    "Custom Field",
    "Property Setter",
    "Workspace",
    "Workflow",
    "Client Script"
]

app_include_js = ["/public/js/instrument_intake_form.js"]