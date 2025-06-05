import frappe
import unittest

class TestRepairRequest(unittest.TestCase):
    def test_insert_repair_request(self):
        doc = frappe.get_doc({
            "doctype": "Repair Request",
            "customer": frappe.db.get_value("Customer", {}, "name"),
            "instrument_type": "Clarinet",
            "serial_number": "CL123456"
        })
        doc.insert(ignore_permissions=True)
        self.assertTrue(doc.name)