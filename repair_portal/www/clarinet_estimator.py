"""Portal route for the clarinet estimator."""

from __future__ import annotations

import frappe
from frappe import _

from repair_portal.service_planning.clarinet_estimator import INSTRUMENT_FAMILIES


def get_context(context: dict) -> dict:
    frappe.only_for(("Customer", "Technician", "Repair Manager", "System Manager"))
    context.title = _("Clarinet Repair Estimator")
    context.instrument_families = INSTRUMENT_FAMILIES
    context.bootstrap_method = "repair_portal.api.estimator.get_bootstrap"
    context.submit_method = "repair_portal.api.estimator.submit"
    return context
