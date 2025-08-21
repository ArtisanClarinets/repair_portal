import frappe
from frappe.tests.utils import FrappeTestCase


class TestClarinetIntake(FrappeTestCase):
	def test_inventory_intake_creates_initial_setup(self):
		intake = frappe.get_doc(
			{
				"doctype": "Clarinet Intake",
				"intake_type": "Inventory",
				"serial_no": "TEST-INV-001",
				"item_code": "CLAR-100",
				"customer": "Test Customer",
			}
		)
		intake.insert()
		intake.submit()
		setup_name = frappe.db.get_value("Clarinet Initial Setup", {"intake": intake.name})
		self.assertTrue(setup_name)
		self.assertEqual(intake.linked_initial_setup, setup_name) # type: ignore
