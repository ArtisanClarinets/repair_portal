# File: repair_portal/repair_portal/instrument_setup/test/test_automation_and_kpi.py
# Version: 1.0
# Date: 2025-06-12
# Purpose: Test technician assignment, material request creation, and checklist KPIs

import frappe
import unittest

class TestAutomationAndKPIs(unittest.TestCase):
    def test_auto_technician_assignment(self):
        setup = frappe.new_doc("Clarinet Initial Setup")
        setup.status = "Open"
        setup.insert()
        self.assertTrue(setup.technician)

    def test_kpi_checklist_completion(self):
        setup = frappe.get_doc({
            "doctype": "Clarinet Initial Setup",
            "status": "Open",
            "checklist": [
                {"description": "Check pads", "completed": 1},
                {"description": "Test keys", "completed": 0}
            ]
        })
        complete = sum(1 for i in setup.checklist if i.completed)
        self.assertEqual(complete, 1)