import frappe
import unittest
from frappe.utils import nowdate
from frappe.exceptions import LinkValidationError

def ensure_user_exists(full_name: str, role: str) -> str:
    """Ensure a user exists with the given full name and role. Returns the User.name."""
    try:
        email = full_name.lower().replace(" ", ".") + "@test.local"
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "send_welcome_email": 0,
            "roles": [{"role": role}]
        })

        existing = frappe.db.get_value("User", {"email": email}, "name")
        if existing:
            return existing

        user.insert(ignore_permissions=True)
        frappe.db.commit()
        return user.name
    except Exception:
        frappe.log_error(title="User Setup Error", message=frappe.get_traceback())
        raise

class TestInventoryIntakeFlow(unittest.TestCase):

    def setUp(self):
        self.received_by = ensure_user_exists("Robby", "Technician")

        if not frappe.db.exists("Brand", "Buffet"):
            frappe.get_doc({"doctype": "Brand", "brand": "Buffet"}).insert()

        if not frappe.db.exists("Customer", "Test Customer"):
            frappe.get_doc({"doctype": "Customer", "customer_name": "Test Customer"}).insert()

        if not frappe.db.exists("Client Profile", {"customer": "Test Customer"}):
            frappe.get_doc({
                "doctype": "Client Profile",
                "customer": "Test Customer",
                "client_name": "Flow Tester"
            }).insert()

    def test_inventory_intake_creates_instrument_and_inspection(self):
        intake = frappe.get_doc({
            "doctype": "Clarinet Intake",
            "intake_type": "Inventory",
            "serial_no": frappe.generate_hash(length=10),
            "customer": "Test Customer",
            "brand": "Buffet",
            "model": "Test Model",
            "instrument_type": "B♭ Clarinet",
            "received_by": self.received_by,
            "received_date": nowdate(),
            "owner": self.received_by
        })
        intake.insert()
        intake.submit()

        instrument_name = frappe.db.get_value("Instrument Profile", {"linked_intake": intake.name})
        self.assertTrue(instrument_name, msg="Instrument Profile was not created.")

        inspection_exists = frappe.db.exists("Quality Inspection", {"reference_name": instrument_name})
        self.assertTrue(inspection_exists, msg="Quality Inspection was not created.")