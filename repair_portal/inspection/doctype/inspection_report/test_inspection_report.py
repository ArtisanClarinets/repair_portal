# Path: inspection/doctype/inspection_report/test_inspection_report.py
# Date: 2025-12-15
# Version: 0.1.0
# Description: Tests for basic Inspection Report behavior

import frappe
from frappe.tests.utils import FrappeTestCase


class TestInspectionReport(FrappeTestCase):
    def test_create_and_defaults(self):
        ir = frappe.get_doc({"doctype": "Inspection Report", "inspection_type": "Clarinet QA"})
        ir.insert(ignore_permissions=True)

        self.assertEqual(ir.status, "Scheduled")

        # Clean up
        frappe.delete_doc("Inspection Report", ir.name, force=True, ignore_permissions=True)
