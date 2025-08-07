import frappe
from frappe.tests.utils import FrappeTestCase


class TestClarinetInitialSetup(FrappeTestCase):
    def test_initial_setup_requires_intake_and_instrument(self):
        setup = frappe.new_doc(
            {
                "doctype": "Clarinet Initial Setup",
                "intake": "TEST-INTAKE-001",
                "instrument_profile": "TEST-INSTR-001",
            }
        )
        # Validate should not throw
        setup.validate()
        # Now test missing intake
        setup_missing = frappe.new_doc(
            {"doctype": "Clarinet Initial Setup", "instrument_profile": "TEST-INSTR-002"}
        )
        with self.assertRaises(frappe.ValidationError):
            setup_missing.validate()
