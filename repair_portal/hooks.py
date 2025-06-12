# repair_portal/hooks.py
# Updated: 2025-06-11
# Version: 1.0.0
# Purpose: Main hook configuration for the Repair Portal app. Includes fixtures and lifecycle hook management for ERPNext.

from __future__ import unicode_literals
import frappe

app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "MRW Artisan Instruments"
app_description = "Clarinet repair management portal"
app_email = "support@artisanclarinets.com"
app_license = "MIT"
app_version = "1.0.0"

# Fixtures auto-detected
fixtures = [
    {"doctype": "Workspace", "filters": [["name", "in", [
        "Enhancements", "Inspection", "Intake", "Instrument Setup", "QA",
        "Repair Logging", "Service Planning", "Tools"]]], "skip_if_empty": 1},
    {"doctype": "Report", "filters": [["ref_doctype", "like", "%"]], "skip_if_empty": 1},
    {"doctype": "Workflow", "filters": [["name", "!=", ""]], "skip_if_empty": 1},
    {"doctype": "Dashboard Chart", "filters": [["name", "!=", ""]], "skip_if_empty": 1},
    {"doctype": "Print Format", "filters": [["name", "!=", ""]], "skip_if_empty": 1}
]

# Removed full_workspace_generate() from after_migrate to avoid workspace JSON deletion
# def after_migrate():
#     from repair_portal.command.full_workspace_generator_v15 import full_workspace_generate
#     full_workspace_generate()
#     frappe.clear_cache()
#     frappe.db.commit()
