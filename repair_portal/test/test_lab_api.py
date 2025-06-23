import frappe
from frappe.tests.utils import FrappeTestCase


class TestLabAPI(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        self.instrument = frappe.get_doc(
            {
                "doctype": "Instrument Profile",
                "instrument_category": "Clarinet",
                "serial_number": "TEST-LAB",
                "brand": "TestBrand",
                "route": "test-lab-inst",
            }
        ).insert()

    def test_save_impedance_snapshot(self):
        result = frappe.get_attr("repair_portal.lab.api.save_impedance_snapshot")(
            instrument=self.instrument.name,
            session_type="Standalone",
            raw_data="[]",
        )
        assert frappe.db.exists("Impedance Snapshot", result["name"])
        child_count = frappe.db.count("Impedance Peak", {"parent": result["name"]})
        self.assertEqual(child_count, 1)

    def test_save_intonation_session(self):
        result = frappe.get_attr("repair_portal.lab.api.save_intonation_session")(
            instrument=self.instrument.name,
            session_type="Standalone",
            raw_data="[]",
        )
        assert frappe.db.exists("Intonation Session", result["name"])

    def test_save_leak_test(self):
        result = frappe.get_attr("repair_portal.lab.api.save_leak_test")(
            instrument=self.instrument.name,
            session_type="Standalone",
            raw_data="[]",
        )
        assert frappe.db.exists("Leak Test", result["name"])

    def test_save_reed_match_result(self):
        result = frappe.get_attr("repair_portal.lab.api.save_reed_match_result")(
            instrument=self.instrument.name,
            session_type="Standalone",
            raw_data="{}",
        )
        assert frappe.db.exists("Reed Match Result", result["name"])

    def test_save_tone_fitness(self):
        result = frappe.get_attr("repair_portal.lab.api.save_tone_fitness")(
            instrument=self.instrument.name,
            session_type="Standalone",
            raw_data="[]",
        )
        assert frappe.db.exists("Tone Fitness", result["name"])

