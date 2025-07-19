# File Header Template
# Relative Path: repair_portal/intake/utils/emailer.py
# Last Updated: 2025-07-05
# Version: v1.0
# Purpose: Centralised helper for all Clarinet-Intake customer notifications.
#          Builds context-rich, translated messages and delivers them through
#          frappe.sendmail—designed to be called in a background job.
# Dependencies: frappe, repair_portal.logger

from __future__ import annotations

import frappe
from frappe import _

from repair_portal.logger import get_logger

LOGGER = get_logger()

# --------------------------------------------------------------------------- #
#  Email copy templates
# --------------------------------------------------------------------------- #
_SUBJECTS: dict[str, str] = {
    "submitted": _("Your instrument has been received – Intake #{name}"),
    "state_change": _("Update on your instrument – Intake #{name}"),
    "completed": _("Your instrument is ready – Intake #{name}"),
}


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
def queue_intake_status_email(intake_name: str, event: str = "state_change") -> None:
    """Build and send a transactional email to a Clarinet-Intake customer.

    Designed for use with ``frappe.enqueue`` so the actual SMTP call runs in a
    background worker—ensuring the Desk UX remains snappy.

    Args:
        intake_name: The ``Clarinet Intake`` primary key.
        event:      Reason for the notification. Supported values:
                    ``submitted`` | ``state_change`` | ``completed``.
    """
    intake = frappe.get_doc("Clarinet Intake", intake_name)

    if not getattr(intake, "customer_email", None):
        LOGGER.warning("Intake %s has no customer_email; skipping notification", intake_name)
        return

    subject = _build_subject(event, intake)
    html_body = _build_message(event, intake)

    try:
        frappe.sendmail(
            recipients=[intake.customer_email],
            subject=subject,
            message=html_body,
            reference_doctype=intake.doctype,
            reference_name=intake.name,
        )
        LOGGER.info(
            "Customer email sent for Intake %s (event=%s) to %s",
            intake_name,
            event,
            intake.customer_email,
        )
    except Exception:
        frappe.log_error(
            title="Clarinet Intake email failure",
            message=frappe.get_traceback(),
        )
        LOGGER.exception(
            "Error while sending customer email for Intake %s (event=%s)",
            intake_name,
            event,
        )


# --------------------------------------------------------------------------- #
#  Internal helpers
# --------------------------------------------------------------------------- #
def _build_subject(event: str, intake) -> str:
    """Return a translated, per-event email subject line."""
    template = _SUBJECTS.get(event, _SUBJECTS["state_change"])
    return template.format(name=intake.name)


def _build_message(event: str, intake) -> str:
    """Compose a minimal, brand-consistent HTML email body."""
    base_url = frappe.utils.get_url()
    intake_url = f"{base_url}/app/clarinet-intake/{intake.name}"

    lines = [
        _("<p>Hi {0},</p>").format(intake.customer_name or _("there")),
    ]

    if event == "submitted":
        lines.append(
            _(
                "<p>We’ve logged your instrument into our system. "
                "You can track progress at any time using the link below.</p>"
            )
        )
    elif event == "completed":
        lines.append(
            _(
                "<p>Great news! Your instrument has passed final checks and is "
                "ready for collection or shipment.</p>"
            )
        )
    else:  # generic workflow update
        lines.append(
            _("<p>Your instrument’s status has been updated to " "<strong>{0}</strong>.</p>").format(
                intake.workflow_state or _("Unknown")
            )
        )

    lines.append(_("<p><a href='{0}'>View your Intake record</a></p>").format(intake_url))
    lines.append(_("<p>Thank you for choosing Artisan Clarinets!</p>"))

    return "\n".join(lines)
