"""Payment Request integration hooks for customer approvals."""

from __future__ import annotations

import frappe
from frappe import _


def handle_payment_request_update(doc, method: str) -> None:  # noqa: D401
    """Dispatch payment confirmation emails when the request is completed."""

    if doc.status not in {"Completed", "Paid"}:
        return
    # Avoid duplicate notifications
    if doc.flags.get("repair_portal_payment_notified"):
        return
    doc.flags["repair_portal_payment_notified"] = True

    customer_name = getattr(doc, "customer", None) or getattr(doc, "party", None)
    recipient = doc.contact_email or doc.email_to
    if not recipient:
        return

    context = {
        "customer_name": customer_name,
        "paid_amount": doc.grand_total or doc.paid_amount,
        "payment_request": doc.name,
    }
    frappe.sendmail(
        recipients=[recipient],
        subject=_("Payment received: {0}").format(doc.name),
        template="payment_received_notification",
        args=context,
        reference_doctype="Payment Request",
        reference_name=doc.name,
        now=True,
    )
