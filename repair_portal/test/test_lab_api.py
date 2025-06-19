import frappe
from frappe.tests.utils import FrappeTestCase


class TestLabAPI(FrappeTestCase):
    def test_save_impedance_snapshot(self):
        frappe.set_user("Administrator")
        result = frappe.get_attr("repair_portal.lab.api.save_impedance_snapshot")(
            instrument="INST-TEST",
            session_type="Standalone",
            raw_data="[]",
        )
        assert frappe.db.exists("Impedance Snapshot", result["name"])
        child_count = frappe.db.count("Impedance Peak", {"parent": result["name"]})
        self.assertEqual(child_count, 1)
