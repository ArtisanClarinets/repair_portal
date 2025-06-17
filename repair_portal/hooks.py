app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "MRW Artisan Instruments"
app_description = "Clarinet Repair System"
app_email = "support@artisanclarinets.com"
app_license = "MIT"

website_generators = [
    "Instrument Profile",
    "Player Profile",
]

portal_menu_items = [
    {"title": "My Instruments", "route": "/my_instruments", "reference_doctype": "Instrument Profile"},
    {"title": "My Repairs", "route": "/my_repairs", "reference_doctype": "Repair Request"},
    {"title": "Technician Dashboard", "route": "/technician_dashboard", "role": "Technician"},
]
