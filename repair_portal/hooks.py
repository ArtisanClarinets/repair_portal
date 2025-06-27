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

after_install = "repair_portal.qa.setup.clarinet_qc.sync_qc"
after_migrate = "repair_portal.qa.setup.clarinet_qc.sync_qc"

website_generators = [
    "Instrument Profile",
    "Player Profile",
]