"""Web controller for Customer Sign-Off page."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import get_url_to_form

login_required = True


def get_context(context):
    frappe.only_for(('Client',))
    repair = frappe.form_dict.get('repair')
    if not repair:
        frappe.throw(_('Repair not specified'))

    context.repair = repair
    context.page_title = _('Customer Sign-Off')
    context.redirect_url = get_url_to_form('Repair Request', repair)
    return context
