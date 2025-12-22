# repair_portal/tests/test_intake_dashboard.py

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.api.intake_dashboard import get_intake_counts, get_recent_intakes


class TestIntakeDashboard(FrappeTestCase):
    def setUp(self):
        # Create user with no access
        self.no_access_user = "no_access@example.com"
        if not frappe.db.exists("User", self.no_access_user):
            user = frappe.new_doc("User")
            user.email = self.no_access_user
            user.first_name = "No Access"
            user.roles = [{"role": "Customer"}] # Assuming customer has no access to Intake
            user.insert(ignore_permissions=True)

        # Create user with access
        self.tech_user = "tech@example.com"
        if not frappe.db.exists("User", self.tech_user):
            user = frappe.new_doc("User")
            user.email = self.tech_user
            user.first_name = "Technician"
            user.roles = [{"role": "Technician"}]
            user.insert(ignore_permissions=True)

        # Create dummy Intake
        if not frappe.db.exists("Clarinet Intake", "TEST-INTAKE-1"):
            doc = frappe.new_doc("Clarinet Intake")
            doc.name = "TEST-INTAKE-1"
            doc.intake_record_id = "TEST-INTAKE-1"
            doc.intake_status = "Pending"
            doc.creation = frappe.utils.now_datetime()
            doc.modified = frappe.utils.now_datetime()
            doc.db_insert()

    def test_permission_denied(self):
        frappe.set_user(self.no_access_user)
        with self.assertRaises(frappe.PermissionError):
            get_intake_counts()

        with self.assertRaises(frappe.PermissionError):
            get_recent_intakes()

    def test_permission_allowed_and_data(self):
        frappe.set_user(self.tech_user)
        # Should not raise
        counts = get_intake_counts()
        self.assertIn("Pending", counts)
        self.assertGreaterEqual(counts["Pending"], 1)

        recent = get_recent_intakes()
        self.assertTrue(isinstance(recent, list))

    def tearDown(self):
        frappe.set_user("Administrator")
        # Cleanup
        if frappe.db.exists("Clarinet Intake", "TEST-INTAKE-1"):
            frappe.delete_doc("Clarinet Intake", "TEST-INTAKE-1", force=True)
