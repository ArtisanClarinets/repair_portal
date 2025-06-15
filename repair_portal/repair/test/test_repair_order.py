# File: repair_portal/repair/test/test_repair_order.py
# Version: 1.0
# Date: 2025-06-15
# Purpose: Tests full Repair Order lifecycle and logic

import frappe
import unittest

class TestRepairOrder(unittest.TestCase):
    def setUp(self):
        self.intake = frappe.get_doc({
            "doctype": "Clarinet Intake",
            "customer": "Test Customer",
            "instrument_type": "Bb Clarinet"
        }).insert()

        self.order = frappe.get_doc({
            "doctype": "Repair Order",
            "intake": self.intake.name,
            "instrument_profile": None,
            "promised_date": frappe.utils.add_days(frappe.utils.today(), -1),
            "repair_tasks": [
                {"task_type": "Crack Repair", "parts_cost": 20.0, "actual_hours": 2.5},
                {"task_type": "Key Refit", "parts_cost": 10.0, "actual_hours": 1.0}
            ]
        }).insert()

    def test_sla_breach_flag(self):
        self.order.reload()
        self.assertTrue(self.order.sla_breached)

    def test_totals_calculated(self):
        self.order.reload()
        self.assertEqual(self.order.total_parts_cost, 30.0)
        self.assertEqual(self.order.total_labor_hours, 3.5)

    def test_status_change_triggers_qa(self):
        self.order.status = "QA"
        self.order.save()
        self.assertTrue(self.order.qa_checklist)

    def tearDown(self):
        frappe.delete_doc("Repair Order", self.order.name)
        frappe.delete_doc("Clarinet Intake", self.intake.name)