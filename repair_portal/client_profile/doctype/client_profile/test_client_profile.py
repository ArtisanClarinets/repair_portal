import frappe
import unittest

class TestClientProfileChildren(unittest.TestCase):
    """Test all linked child trackers load correctly."""

    def setUp(self):
        # Load a recent Client Profile if available
        profiles = frappe.get_all("Client Profile", limit=1, order_by="modified desc")
        self.client_profile = frappe.get_doc("Client Profile", profiles[0].name) if profiles else None

    def test_child_tables_load(self):
        if not self.client_profile:
            self.skipTest("No Client Profile found")

        for child_field in [
            "owned_instruments",
            "linked_players",
            "repair_logs",
            "qa_findings",
            "tone_sessions",
            "setup_logs",
            "leak_tests"
        ]:
            self.assertIsInstance(getattr(self.client_profile, child_field), list)

    # def tearDown(self):
    #     pass  # optional cleanup here