# File: repair_portal/inspection/doctype/inspection_report/test_inspection_report.py
# Updated: 2025-06-27
# Purpose: Unit tests for Inspection Report DocType
import unittest

import frappe


class TestInspectionReport(unittest.TestCase):
    def test_report_creation_with_checklist(self):
        doc = frappe.new_doc("Inspection Report")
        doc.inspection_date = frappe.utils.nowdate()
        doc.instrument_id = "CL-0001"
        doc.customer_name = "Test Customer"
        doc.inspection_type = "Clarinet QA"
        doc.status = "Scheduled"
        doc.procedure = "QC Pad Seal Top Joint"
        doc.insert()
        self.assertTrue(doc.name)
        doc.delete()
