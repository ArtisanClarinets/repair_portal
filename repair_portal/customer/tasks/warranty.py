"""Warranty and aftercare reminder jobs."""

from __future__ import annotations

from typing import List

import frappe
from frappe import _
from frappe.utils import add_days, getdate

LOGGER = frappe.logger("warranty_aftercare")
REMINDER_SUBJECT = "Warranty service reminder"


def dispatch_warranty_reminders(days_ahead: int = 30) -> List[str]:
    """Send reminders for warranties ending within ``days_ahead`` days.

    Returns a list of instrument profile names that received notifications.
    """

    today = getdate()
    deadline = add_days(today, days_ahead)
    profiles = frappe.get_all(
        "Instrument Profile",
        filters={
            "warranty_end_date": ["between", [today, deadline]],
            "disabled": ["!=", 1],
        },
        fields=["name", "customer", "warranty_end_date"],
    )
    notified: List[str] = []
    for profile in profiles:
        if _already_notified(profile.name, today):
            continue
        recipient = _get_customer_email(profile.customer)
        if not recipient:
            LOGGER.warning("Skipping warranty reminder for %s: missing email", profile.name)
            continue
        context = {
            "profile_name": profile.name,
            "warranty_end_date": profile.warranty_end_date,
            "days_remaining": (getdate(profile.warranty_end_date) - today).days,
        }
        frappe.sendmail(
            recipients=[recipient],
            subject=_("Warranty ending soon: {0}").format(profile.name),
            template="warranty_reminder",
            args=context,
            reference_doctype="Instrument Profile",
            reference_name=profile.name,
            now=True,
        )
        _record_notification(profile.name, today)
        notified.append(profile.name)
        LOGGER.info("Sent warranty reminder for %s", profile.name)
    if not notified:
        LOGGER.info("No warranty reminders due on %s", today)
    return notified


def _already_notified(profile_name: str, notice_date) -> bool:
    return frappe.db.exists(
        "Comment",
        {
            "comment_type": "Info",
            "reference_doctype": "Instrument Profile",
            "reference_name": profile_name,
            "subject": ["=", f"Warranty reminder {notice_date}"],
        },
    )


def _record_notification(profile_name: str, notice_date) -> None:
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Instrument Profile",
            "reference_name": profile_name,
            "subject": f"Warranty reminder {notice_date}",
            "content": _( "Automated warranty reminder dispatched."),
        }
    ).insert(ignore_permissions=True)


def _get_customer_email(customer: str | None) -> str | None:
    if not customer:
        return None
    email = frappe.db.get_value("Customer", customer, "email_id")
    if email:
        return email
    contact = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Customer",
            "link_name": customer,
            "parenttype": "Contact",
        },
        fields=["parent"],
        limit=1,
    )
    if not contact:
        return None
    return frappe.db.get_value("Contact", contact[0].parent, "email_id")
