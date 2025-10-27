"""Repair estimate approval portal."""
from __future__ import annotations

from typing import Any, Dict

import frappe
from frappe import _
from werkzeug.exceptions import NotFound

from repair_portal.repair_portal.api.portal import prepare_quote_and_deposit
from repair_portal.repair_portal.utils import token as token_utils


def get_context(context: Dict[str, Any]) -> Dict[str, Any]:
    name = frappe.form_dict.get("name")
    token = frappe.form_dict.get("token")
    if not name or not token:
        raise NotFound()
    estimate = frappe.get_doc("Repair Estimate", name)
    if not token_utils.verify_token(estimate.approval_token, token, f"repair-estimate:{estimate.name}"):
        raise NotFound()
    template = frappe.get_doc("Repair Class Template", estimate.repair_class) if estimate.repair_class else None
    upsell_options = template.get("upsell_options") if template else []
    context.update(
        {
            "no_cache": 1,
            "show_sidebar": False,
            "title": _("Repair Estimate"),
            "estimate": estimate,
            "token": token,
            "upsell_options": upsell_options,
        }
    )
    return context


@frappe.whitelist(allow_guest=True)
def submit_quote_decision(estimate: str, token: str, upsells: str | None = None) -> Dict[str, Any]:
    doc = frappe.get_doc("Repair Estimate", estimate)
    if not token_utils.verify_token(doc.approval_token, token, f"repair-estimate:{doc.name}"):
        raise NotFound()
    if not doc.repair_order:
        frappe.throw(_("Repair order reference is required to process the estimate."))
    response = prepare_quote_and_deposit(
        repair_order=doc.repair_order,
        repair_class=doc.repair_class,
        upsells=upsells,
        approval_token=token,
    )
    return response
