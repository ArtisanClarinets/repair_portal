import unittest

import frappe


class TestInstrumentWellness(unittest.TestCase):
    def test_page_context(self):
        frappe.set_user("Administrator")
        inst = frappe.get_doc(
            {
                "doctype": "Instrument Profile",
                "instrument_category": "Clarinet",
                "serial_number": "TEST123",
                "brand": "TestBrand",
                "route": "test-inst",
            }
        ).insert()
        context = frappe._dict()
        frappe.local.form_dict = {"name": inst.name}
        from repair_portal.www import instrument_wellness

        instrument_wellness.get_context(context)
        assert context.instrument.name == inst.name
