# relative path: intake/page/intake_master_console/utils.py
# updated: 2025-07-01
# version: 1.1
# purpose: Backend utility to fetch console data for the Intake Master Console

import frappe
from frappe.utils import escape_html


def get_console_data():
    intakes = frappe.get_all(
        "Clarinet Intake",
        fields=["name", "customer", "instrument_profile", "status", "modified"],
        limit=50,
        order_by="modified desc",
    )

    rows = []
    for d in intakes:
        rows.append(
            {
                "name": escape_html(d.name),
                "customer": escape_html(d.customer),
                "instrument": escape_html(d.instrument_profile or ""),
                "status": escape_html(d.status or ""),
                "modified": escape_html(d.modified),
            }
        )

    return frappe.render_template(
        "repair_portal/intake/page/intake_master_console/console_table.html", {"rows": rows}
    )
