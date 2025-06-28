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

after_install = [ 
    "repair_portal.qa.setup.clarinet_qc.sync_qc",
    "repair_portal.scripts.reload_all_doctypes.reload_all_doctypes"
]
after_migrate = [ 
    "repair_portal.scripts.hooks.fix_workflow_states.fix_workflow_states",
    "repair_portal.scripts.hooks.fix_name_key.run",
    "repair_portal.scripts.hooks.insert_workflows.insert_workflows_from_json",
    "repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes"
]

website_generators = [
    "Instrument Profile",
    "Player Profile",
]
