# repair_portal/hooks.py
# Updated: 2025-06-12
# Version: 1.1.0
# Purpose: Main hook configuration for the Repair Portal app. Includes fixtures and lifecycle hook management for ERPNext.

from __future__ import unicode_literals
import frappe

app_name = "repair_portal"
app_title = "Repair Portal"
app_publisher = "MRW Artisan Instruments"
app_description = "Clarinet repair management portal"
app_email = "support@artisanclarinets.com"
app_license = "MIT"
app_version = "1.1.0"

# Fixtures auto-detected and extended
fixtures = [
    {"doctype": "Workspace", "filters": [["name", "in", [
        "Enhancements", "Inspection", "Intake", "Instrument Setup", "QA",
        "Repair Logging", "Service Planning", "Tools"]]], "skip_if_empty": 1},
    {"doctype": "Report", "filters": [["ref_doctype", "like", "%"]], "skip_if_empty": 1},
    {"doctype": "Workflow", "filters": [["name", "!=", ""]], "skip_if_empty": 1},
    {"doctype": "Dashboard Chart", "filters": [["is_public", "=", 1]]},
    {"doctype": "Print Format", "filters": [["name", "!=", ""]], "skip_if_empty": 1},
    {"doctype": "Notification", "filters": [["enabled", "=", 1]]},
    {"doctype": "Role"},
    {"doctype": "Role Profile"},
    {"doctype": "Custom Field"},
    {"doctype": "Property Setter"},
    {"doctype": "Client Script", "filters": [["enabled", "=", 1]]}
]

# Note: full_workspace_generate() removed from after_migrate due to overwriting risk