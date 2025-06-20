# File: repair_portal/instrument_profile/doctype/instrument_insurance_report/instrument_insurance_report.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Generates insurance PDF reports for instruments including service history and valuation

import frappe
from frappe.model.document import Document

class InstrumentInsuranceReport(Document):
    def validate(self):
        if not self.report_date:
            self.report_date = frappe.utils.nowdate()

    def on_submit(self):
        frappe.msgprint("Insurance Report generated and submitted.")