# File: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Created: 2025-06-13
# Version: 1.0
# Purpose: Controller logic for Instrument Profile DocType

import frappe
from frappe.model.document import Document

class InstrumentProfile(Document):
    """Server side logic for the Instrument Profile DocType."""

    #: configuration used by Frappe's website renderer
    website = frappe._dict(
        # the field that controls whether the record should be shown on the website
        # all instrument profiles are considered published when they exist
        condition_field="name",
        # use the instrument's serial number as the web page title
        page_title_field="serial_number",
    )

    def validate(self):
        if self.acquisition_type == "Customer" and not self.customer:
            frappe.throw("Customer is required for customer-owned instruments.")

    def on_submit(self):
        frappe.msgprint("Instrument profile submitted successfully.")
