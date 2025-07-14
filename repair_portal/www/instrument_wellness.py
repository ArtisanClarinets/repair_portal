"""Show wellness dashboard for a specific instrument."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate

login_required = True


def get_context(context):
    """Build context for instrument wellness dashboard."""
    frappe.only_for(("Client", "Technician"))

    name = frappe.form_dict.get("name")
    instrument = None
    logs = []
    wellness_score = 0
    due_days = None

    if name:
        try:
            instrument = frappe.get_doc("Instrument Profile", name)

            user = frappe.session.user

            # Permissions: Clients can only see their own instruments
            if "Technician" not in frappe.get_roles(user):
                client = frappe.db.get_value("Client Profile", {"linked_user": user}, "name")
                if instrument.client_profile != client and instrument.owner != user:
                    frappe.throw(_("Not permitted."))

            logs = frappe.get_all(
                "Clarinet Repair Log",
                filters={"clarinet_serial_no": instrument.serial_no},
                fields=["name", "repair_type", "modified"],
                order_by="modified desc",
            )

            wellness_score = instrument.wellness_score or 0

            if instrument.last_service_date:
                next_due = add_days(instrument.last_service_date, 180)
                due_days = (getdate(next_due) - getdate(nowdate())).days

        except frappe.DoesNotExistError:
            frappe.msgprint(_("Instrument not found."))

    context.instrument = instrument
    context.service_logs = logs
    context.service_logs_json = frappe.safe_json.dumps(logs)
    context.wellness_score = wellness_score
    context.due_days = due_days

    return context
