app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "MRW Artisan Instruments"
app_description = "Clarinet Repair System"
app_email = "support@artisanclarinets.com"
app_license = "MIT"

app_include_js = [
    "/assets/repair_portal/lab_bundle.js",
    "https://cdn.jsdelivr.net/npm/plotly.js-dist@2.26.0/plotly.min.js",
    "https://cdn.jsdelivr.net/npm/meyda/dist/web/meyda.min.js",
    "https://cdn.jsdelivr.net/npm/tone/build/Tone.min.js",
]

website_generators = [
    "Instrument Profile",
    "Player Profile",
]

portal_menu_items = [
    {"title": "My Instruments", "route": "/my_instruments", "reference_doctype": "Instrument Profile"},
    {"title": "My Repairs", "route": "/my_repairs", "reference_doctype": "Repair Request"},
    {"title": "My Players", "route": "/my_players", "reference_doctype": "Player Profile"},
    {"title": "Technician Dashboard", "route": "/technician_dashboard", "role": "Technician"},
]
