# File Header Template
# Relative Path: repair_portal/customer/doctype/instruments_owned/instruments_owned.py
# Last Updated: 2025-07-16
# Version: v2.0
# Purpose: Refactored child table to support Customer linkage in ERPNext-native architecture
# Dependencies: Customer, Serial No
from __future__ import annotations
import frappe
from frappe.model.document import Document


class InstrumentsOwned(Document):
    def validate(self):
        if not self.customer:  # type: ignore
            frappe.throw('Customer link is required for Instruments Owned entry.')
