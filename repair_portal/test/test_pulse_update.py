import unittest

import frappe

from repair_portal.repair_portal.doctype.pulse_update import pulse_update


class TestPulseUpdateAPI(unittest.TestCase):
    def test_create_update(self):
        frappe.set_user("Administrator")
        req = frappe.get_doc({
            "doctype": "Repair Request",
            "customer": "test@example.com",
            "issue_description": "test issue",
        }).insert()
        name = pulse_update.create_update(
            repair_request=req.name,
            status="Init",
            details="Started",
            percent_complete=10,
        )
        assert frappe.db.exists("Pulse Update", name)
