# relative path: repair_portal/hooks.py
# date updated: 2025-07-18
# version: 1.1.0
# purpose: App configuration hooks and fixtures declaration (Updated for Intake JS split)
# notes: Added doctype_js for Clarinet Intake mode-specific scripts

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
]

app_include_js = [
    "/public/js/client_portal/client_portal.bundle.js",
    "/public/js/technician_dashboard/technician_dashboard.bundle.js",
    "/public/js/technician_dashboard/index.dum.js",
    "/public/js/recording_analyzer.bundle.js",
    "/public/js/intonation_recorder.bundle.js",
    "/public/js/client_portal/customer/customer.bundle.js",
]

after_install = [
    "repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes",
]
after_migrate = ["repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes"]

doc_events = {
    "Repair Order": {
        "on_submit": "repair_portal.repair_order.doctype.repair_order.repair_order.RepairOrder.on_submit",
        "on_cancel": "repair_portal.repair_order.doctype.repair_order.repair_order.RepairOrder.on_cancel",
    },
    # ─── Clarinet Intake automation ───────────────────────────────────────
    "Clarinet Intake": {
        # Create Serial No immediately after insert (draft) **and** on_submit (final).
        "after_insert": (
            "repair_portal.intake.doctype.clarinet_intake.clarinet_intake_serial.create_serial_no"
        ),
        "on_submit": (
            "repair_portal.intake.doctype.clarinet_intake.clarinet_intake_serial.create_serial_no"
        ),
    },
}


