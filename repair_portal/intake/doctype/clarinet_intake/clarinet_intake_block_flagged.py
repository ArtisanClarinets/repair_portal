# --------------------------------------------------------------------------- #
# File    : clarinet_intake_block_flagged.py
# Version : v1.3.0 — 2025-07-07
# Purpose : Block edit / cancel / delete when workflow_state == "Flagged".
# Changelog:
#   • Replaced removed helper `frappe.db.set` → `frappe.db.set_value`
#     (see v15 migration notes) — no behavioural change.
#   • Added a short docstring & minor typing hints (optional).
# --------------------------------------------------------------------------- #

from __future__ import annotations
import logging
import frappe
from frappe import _

LOG = frappe.logger("repair_portal.block_flagged", allow_site=True)
LOG.setLevel(logging.INFO)


def _err(msg: str, title: str) -> None:
    """Log + create an Error Log entry that is visible in the Desk."""
    LOG.error(msg)
    frappe.log_error(msg, title)


# ── hooks ──────────────────────────────────────────────────────────
def before_save(doc) -> None:  # noqa: N802
    if doc.workflow_state == "Flagged":
        _err(f"Edit blocked on flagged intake {doc.name}", "Flagged Intake Edit")
        frappe.throw(_("Editing is not allowed while intake is Flagged."))


def before_cancel(doc) -> None:  # noqa: N802
    if doc.workflow_state == "Flagged":
        _err(f"Cancel blocked on flagged intake {doc.name}", "Flagged Intake Cancel")
        frappe.throw(_("Canceling a flagged intake is prohibited."))


def on_trash(doc) -> None:  # noqa: N802
    if doc.workflow_state == "Flagged":
        _err(f"Delete blocked on flagged intake {doc.name}", "Flagged Intake Delete")
        frappe.throw(_("Deleting a flagged intake is not allowed."))

    # Friendly notices for linked docs
    if getattr(doc, "instrument_profile", None):
        frappe.msgprint(
            _("Instrument Profile {0} linked to this Intake will remain intact.").format(
                doc.instrument_profile
            )
        )
    if getattr(doc, "loaner_agreement", None):
        frappe.msgprint(
            _("Loaner Agreement {0} linked to this Intake will remain intact.").format(
                doc.loaner_agreement
            )
        )

    # Optionally mark checklist items completed
    if frappe.db.exists("Intake Checklist Item", {"parent": doc.name}):
        # v15-safe replacement for the old frappe.db.set(...)
        frappe.db.set_value(
            "Intake Checklist Item",
            {"parent": doc.name},        # filters
            {"status": "Completed"},     # column(s) to update
        )