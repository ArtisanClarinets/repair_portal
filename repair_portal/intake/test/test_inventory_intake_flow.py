import frappe
from frappe.tests.utils import FrappeTestCase

class TestInventoryIntakeFlow(FrappeTestCase):
    def test_inventory_intake_links_initial_setup(self):
        intake = frappe.get_doc({
            "doctype": "Clarinet Intake",
            "intake_type": "Inventory",
            "serial_no": "TEST-INV-002",
            "item_code": "CLAR-200",
            "customer": "Test Customer"
        })
        intake.insert()
        intake.submit()
        setup = frappe.get_doc("Clarinet Initial Setup", intake.linked_initial_setup)
        self.assertEqual(setup.intake, intake.name)
        self.assertEqual(setup.instrument_profile, intake.instrument_profile)
