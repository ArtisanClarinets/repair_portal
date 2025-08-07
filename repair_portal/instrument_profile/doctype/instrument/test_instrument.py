# Copyright (c) 2025, DT and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestInstrument(FrappeTestCase):
    def test_instrument_id_autoname(self):
        """Test auto-generation of instrument_id pattern"""
        serial = frappe.generate_hash(length=6)
        doc = frappe.get_doc({
            "doctype": "Instrument",
            "serial_no": serial,
            "instrument_type": "B\u266d Clarinet",
            "clarinet_type": "B\u266d Clarinet",
            "instrument_category": None
        })
        doc.insert(ignore_permissions=True)
        self.assertTrue(doc.instrument_id.startswith("INST-"))
        self.assertTrue(doc.instrument_id.endswith(serial))
        self.assertEqual(len(doc.instrument_id.split("-")), 3)
        frappe.delete_doc("Instrument", doc.name)

    def test_no_duplicate_serial_no(self):
        serial = frappe.generate_hash(length=6)
        doc1 = frappe.get_doc({
            "doctype": "Instrument",
            "serial_no": serial,
            "instrument_type": "A Clarinet",
            "clarinet_type": "A Clarinet",
            "instrument_category": None
        })
        doc1.insert(ignore_permissions=True)
        with self.assertRaises(frappe.ValidationError):
            doc2 = frappe.get_doc({
                "doctype": "Instrument",
                "serial_no": serial,
                "instrument_type": "Bass Clarinet",
                "clarinet_type": "Bass Clarinet",
                "instrument_category": None
            })
            doc2.insert(ignore_permissions=True)
        frappe.delete_doc("Instrument", doc1.name)
