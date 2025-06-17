# File: repair_portal/www/pad_map.py
# Updated: 2025-06-16
# Version: 1.0
# Purpose: Controller for /pad-map/<docname> to display pad map SVG and status info

import frappe


@frappe.whitelist(allow_guest=True)
def get_context(context):
    docname = frappe.form_dict.get("name")
    if not docname:
        frappe.throw("Missing repair log ID")

    repair_log = frappe.get_doc("Clarinet Repair Log", docname)
    svg_path = frappe.get_site_path("public", "assets", "repair_portal", "images", "svg_pad_maps", "clarinet_upper_joint.svg")

    try:
        with open(svg_path) as f:
            svg_content = f.read()
    except Exception:
        svg_content = ""

    pad_data = [
        {
            "pad_id": pad.pad_id,
            "pad_name": pad.pad_name,
            "status": pad.status
        }
        for pad in repair_log.pad_conditions
    ]

    context.svg_content = svg_content
    context.pad_data = pad_data
    return context