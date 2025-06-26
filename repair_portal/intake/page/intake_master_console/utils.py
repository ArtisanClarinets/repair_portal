# relative path: intake/page/intake_master_console/utils.py
# updated: 2025-06-15
# version: 1.0
# purpose: Backend utility to fetch console data for the Intake Master Console

import frappe


def get_console_data():
    intakes = frappe.get_all(
        "Clarinet Intake",
        fields=["name", "customer", "instrument_profile", "status", "modified"],
        limit=50,
        order_by="modified desc",
    )

    html = "<table class='table table-bordered'><thead><tr><th>ID</th><th>Customer</th><th>Instrument</th><th>Status</th><th>Last Modified</th></tr></thead><tbody>"
    for d in intakes:
        html += f'<tr><td>{d.name}</td><td>{d.customer}</td><td>{d.instrument_profile or ""}</td><td>{d.status or ""}</td><td>{d.modified}</td></tr>'
    html += "</tbody></table>"

    return html
