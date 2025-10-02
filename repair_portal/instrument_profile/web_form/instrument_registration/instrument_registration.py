# Path: repair_portal/instrument_profile/web_form/instrument_registration/instrument_registration.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Web form controller for customer instrument registration; handles context and prefill logic
# Dependencies: frappe

import frappe
from frappe import _


def get_context(context):
    """Prepare context for instrument registration web form"""
    context.no_cache = 1
    context.show_sidebar = False
    return context
