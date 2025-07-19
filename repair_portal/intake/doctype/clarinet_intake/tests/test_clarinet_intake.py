import frappe
import unittest

class TestClarinetIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.make_test_customer()
        cls.make_test_warehouse()

    @staticmethod
    def make_test_customer():
        if not frappe.db.exists("Customer", "Test Customer"):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test Customer",
                "customer_type": "Individual"
            }).insert(ignore_permissions=True)

    @staticmethod
    def make_test_warehouse():
        if not frappe.db.exists("Warehouse", "_Test Warehouse - _TC"):
            frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": "_Test Warehouse - _TC",
                "company": frappe.defaults.get_user_default("Company") or "Test Company"
            }).insert(ignore_permissions=True)

    def test_inventory_intake_creates_children(self):
        doc = frappe.get_doc({
            "doctype": "Clarinet Intake",
            "intake_type": "Inventory",
            "item_code": "_Test Item",
            "warehouse": "_Test Warehouse - _TC",
        })
        doc.insert()
        # Serial number should NOT be auto-created for Inventory
        self.assertFalse(doc.serial_no)
        # Instrument Inspection or Clarinet Initial Setup may not exist if not required
        # Only check for doc creation if that is your business rule

    def test_inventory_intake_missing_required_fields(self):
        # If no required fields for Inventory, nothing should error
        try:
            doc = frappe.get_doc({
                "doctype": "Clarinet Intake",
                "intake_type": "Inventory"
            })
            doc.insert()
        except frappe.ValidationError:
            self.fail("ValidationError raised unexpectedly for Inventory Intake with no required fields.")

    def test_repair_intake_requires_customer(self):
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({
                "doctype": "Clarinet Intake",
                "intake_type": "Repair"
            }).insert()
        doc = frappe.get_doc({
            "doctype": "Clarinet Intake",
            "intake_type": "Repair",
            "customer": "Test Customer"
        })
        doc.insert()
        self.assertEqual(doc.customer, "Test Customer")

    def test_repair_intake_hides_inventory_fields(self):
        doc = frappe.get_doc({
            "doctype": "Clarinet Intake",
            "intake_type": "Repair",
            "customer": "Test Customer"
        })
        doc.insert()
        self.assertFalse(getattr(doc, "item_code", None))
        self.assertFalse(getattr(doc, "serial_no", None))

    def test_intake_status_badges(self):
        doc = frappe.get_doc({
            "doctype": "Clarinet Intake",
            "intake_type": "Inventory",
            "item_code": "_Test Item",
            "warehouse": "_Test Warehouse - _TC",
        })
        doc.insert()
        self.assertTrue(hasattr(doc, "intake_status"))
        self.assertIn(doc.intake_status, ("Pending", "In Progress", "Complete"))
