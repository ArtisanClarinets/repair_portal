import frappe
from frappe import _

def before_save(doc):
    """Prevent edits if intake is flagged."""
    if doc.workflow_state == "Flagged":
        frappe.throw(_("Editing is not allowed while intake is Flagged."))

def before_cancel(doc):
    """Prevent cancels if intake is flagged."""
    if doc.workflow_state == "Flagged":
        frappe.throw(_("Canceling a flagged intake is prohibited."))

def on_trash(doc):
    """Prevent deletion if intake is flagged and optionally clear linked references."""
    if doc.workflow_state == "Flagged":
        frappe.throw(_("Deleting a flagged intake is not allowed."))

    if doc.instrument_profile:
        ip_doc = frappe.get_doc("Instrument Profile", doc.instrument_profile)
        frappe.msgprint(
            _("Instrument Profile {0} linked to this Intake will remain intact.").format(ip_doc.name)
        )

    if doc.loaner_agreement:
        frappe.msgprint(
            _("Loaner Agreement {0} linked to this Intake will remain intact.").format(doc.loaner_agreement)
        )

    frappe.db.set_value(
        "Intake Checklist Item",
        {"parent": doc.name},
        "status",
        "Completed"
    )
