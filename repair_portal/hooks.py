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
    {"title": "Dashboard", "route": "/me", "reference_doctype": "Client Profile"},
    {"title": "Players", "route": "/my_players", "reference_doctype": "Player Profile"},
    {"title": "Instruments", "route": "/my_instruments", "reference_doctype": "Instrument Profile"},
    {"title": "Create Player", "route": "/app/player-profile/new"},
    {"title": "Settings / Sign Out", "route": "/me?edit=1"},
]
