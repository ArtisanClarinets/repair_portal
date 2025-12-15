# relative path: repair_portal/hooks.py
# date updated: 2025-07-28
# version: 4.1.0
# purpose: App configuration hooks,
# notes: Added doctype_js for Clarinet Intake mode-specific scripts

# doc_events to link child docs -> Repair Order
from repair_portal.repair import utils as _repair_utils  # noqa: F401

export_python_type_annotations = True
app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "Dylan Thompson"
app_description = "Portals for the Repair Portal App"
app_email = "info@artisanclarinets.com"
app_license = "mit"

required_apps = ["frappe", "erpnext"]


fixtures = [
    {"doctype": "Role", "filters": [["role_name", "in", [
        "Intake Coordinator",
        "Owner/Admin",
        "Front Desk",
        "Repair Technician",
        "Inventory",
        "Ecommerce/Marketing",
        "Accounting",
        "School/Teacher",
        "Customer"
    ]] ]},
    {"doctype": "Email Group", "filters": [["title", "=", "Player Newsletter"]]},
    {"doctype": "Series", "filters": [["name", "in", ["PLAYER-"]]]},
    {"doctype": "Clarinet Estimator Pricing Rule"},
]

doctype_js = {
    "Repair Order": "repair_portal/repair/doctype/repair_order/repair_order.js",
}

portal_menu_items = [
    {"title": "Mail-In Repair", "route": "/mail-in-repair", "role": "Customer"},
    {"title": "Service Plans", "route": "/service-plans", "reference_doctype": "Service Plan Enrollment"},
    {"title": "Teacher Portal", "route": "/teacher-portal", "role": "School/Teacher"},
    {"title": "Scan Tag", "route": "/scan", "role": "Repair Technician"},
]

has_permission = {
    "Mail In Repair Request": "repair_portal.repair_portal.permissions.mail_in_request.has_permission",
    "Repair Order": "repair_portal.repair_portal.permissions.repair_order.has_permission",
    "Instrument": "repair_portal.repair_portal.permissions.instrument.has_permission",
    "Clarinet Intake": "repair_portal.repair_portal.permissions.clarinet_intake.has_permission",
    "Repair Estimate": "repair_portal.repair_portal.permissions.repair_estimate.has_permission",
    "Rental Contract": "repair_portal.repair_portal.permissions.rental_contract.has_permission",
    "Service Plan Enrollment": "repair_portal.repair_portal.permissions.service_plan_enrollment.has_permission",
}

# fire this before any DDL, patches or fixtures run
before_install = [
    "repair_portal.install.seed_email_groups.ensure_email_groups",
    "repair_portal.install.check_setup_complete",
    "repair_portal.install.seed_item_groups_after_migrate",
]

after_install = [
    "repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes",
    "repair_portal.install.seed_all_from_schemas",
    "repair_portal.install.create_custom_fields",
    "repair_portal.utils.install.install_consent_artifacts.install_or_update_consent_artifacts",
]

after_migrate = [
    "repair_portal.scripts.hooks.reload_all_doctypes.reload_all_doctypes",
    # use if update schemas in scripts/hooks/schemas/*
    #   "repair_portal.install.seed_item_groups_after_migrate",
    "repair_portal.install.seed_all_from_schemas",
    # Ensure Consent Artifacts are installed/updated
    # 'repair_portal.utils.install.ensure_workflow_prereqs.ensure_workflow_prereqs',
    "repair_portal.utils.install.install_consent_artifacts.install_or_update_consent_artifacts",
    "repair_portal.patches.post_install.001_fix_player_profile_settings_email_group.execute",
]


doc_events = {
    "Repair Order": {
        "validate": [
            "repair_portal.repair_portal.utils.barcode.ensure_repair_order_barcode"
        ],
        "before_submit": "repair_portal.repair_portal.inventory.material_planner.before_submit",
        "on_submit": [
            "repair_portal.repair.doctype.repair_order.repair_order.RepairOrder.on_submit",
            "repair_portal.repair_portal.inventory.material_planner.on_submit"
        ],
        "on_cancel": "repair_portal.repair.doctype.repair_order.repair_order.RepairOrder.on_cancel"
    },
    "Clarinet Intake": {
        # after_insert will call our new function
        "after_insert": (
            "repair_portal.intake.doctype.clarinet_intake" + ".clarinet_intake_timeline.add_timeline_entries"
        ),
        "validate": [
            "repair_portal.repair.utils.on_child_validate",
            "repair_portal.repair_portal.utils.barcode.ensure_clarinet_intake_barcode"
        ],
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Instrument": {
        "validate": "repair_portal.repair_portal.utils.barcode.ensure_instrument_barcode",
        "after_insert": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_update": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_change": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
    },
    "Instrument Profile": {
        "after_insert": "repair_portal.instrument_profile.events.utils.create_linked_documents",
    },
    "Instrument Serial Number": {
        "on_update": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
    },
    # Optional handlers if these doctypes exist in your app/site:
    "Instrument Condition Record": {
        "after_insert": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_update": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_trash": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
    },
    "Instrument Media": {
        "after_insert": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_trash": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
    },
    "Instrument Interaction Log": {
        "after_insert": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
        "on_trash": "repair_portal.instrument_profile.services.profile_sync.on_linked_doc_change",
    },
    # End Optional handlers
    "Instrument Inspection": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Service Plan": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Repair Estimate": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Final QA Checklist": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Measurement Session": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Diagnostic Metrics": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Repair Task": {
        "validate": "repair_portal.repair.utils.on_child_validate",
        "on_update": "repair_portal.repair.utils.on_child_validate",
    },
    "Sales Invoice": {
        "before_insert": "repair_portal.repair_portal.utils.pos.suggest_repair_class_upsells",
    },
    "Stock Entry": {
        "after_submit": "repair_portal.repair.hooks_stock_entry.after_submit_stock_entry",
    },
    "Payment Request": {},
}


scheduler_events = {
    "hourly": [
        "repair_portal.core.tasks.sla_breach_scan",
        "repair_portal.core.tasks.finalize_billing_packets",
        "repair_portal.repair_portal.service_plans.automation.process_autopay",
    ],
    "daily": [
        "repair_portal.intake.tasks.cleanup_intake_sessions",
        "repair_portal.core.tasks.send_feedback_requests",
        "repair_portal.customer.tasks.warranty.dispatch_warranty_reminders",
        "repair_portal.repair_portal.service_plans.automation.queue_renewal_notifications",
        "repair_portal.repair_portal.utils.compliance.anonymize_closed_repairs",
    ],
}

website_route_rules = [
    {"from_route": "/repair-status/<portal_token>", "to_route": "repair-status"},
    {"from_route": "/quote/<name>", "to_route": "quote"},
    {"from_route": "/scan", "to_route": "scan"},
]

