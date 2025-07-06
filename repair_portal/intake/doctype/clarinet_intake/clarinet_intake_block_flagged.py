# File    : clarinet_intake_block_flagged.py
# Version : v1.2.0 — 2025-07-07
# Purpose : Block edit / cancel / delete when workflow_state == "Flagged".

import logging, frappe
from frappe import _

LOG = frappe.logger("repair_portal.block_flagged", allow_site=True)
LOG.setLevel(logging.INFO)

def _err(msg: str, title: str):
    LOG.error(msg)
    frappe.log_error(msg, title)

# ── hooks ──────────────────────────────────────────────────────────
def before_save(doc):
    if doc.workflow_state == "Flagged":
        _err(f"Edit blocked on flagged intake {doc.name}",
             "Flagged Intake Edit")
        frappe.throw(_("Editing is not allowed while intake is Flagged."))

def before_cancel(doc):
    if doc.workflow_state == "Flagged":
        _err(f"Cancel blocked on flagged intake {doc.name}",
             "Flagged Intake Cancel")
        frappe.throw(_("Canceling a flagged intake is prohibited."))

def on_trash(doc):
    if doc.workflow_state == "Flagged":
        _err(f"Delete blocked on flagged intake {doc.name}",
             "Flagged Intake Delete")
        frappe.throw(_("Deleting a flagged intake is not allowed."))

    # Friendly notices for linked docs
    if getattr(doc, "instrument_profile", None):
        frappe.msgprint(
            _("Instrument Profile {0} linked to this Intake will remain intact.")
            .format(doc.instrument_profile)
        )
    if getattr(doc, "loaner_agreement", None):
        frappe.msgprint(
            _("Loaner Agreement {0} linked to this Intake will remain intact.")
            .format(doc.loaner_agreement)
        )

    # Optionally mark checklist items completed
    if frappe.db.exists("Intake Checklist Item", {"parent": doc.name}):
        frappe.db.set("Intake Checklist Item",
                      {"parent": doc.name},
                      {"status": "Completed"})