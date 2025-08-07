import frappe
from frappe.tests.utils import FrappeTestCase


class TestClarinetIntake(FrappeTestCase):
    def setUp(self):
        self.serial_no = frappe.get_doc(
            {
                "doctype": "Serial No",
                "serial_no": "TST-CLIN-0001",
                "item_code": "TST-ITEM",
                "status": "Active",
            }
        ).insert(ignore_permissions=True)

    def tearDown(self):
        frappe.db.delete("Instrument Inspection", {"serial_no": self.serial_no.serial_no})
        frappe.delete_doc("Serial No", self.serial_no.name, force=1)
        frappe.db.commit()

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #

    def _make_intake(self, **overrides):
        base = dict(
            doctype="Clarinet Intake",
            intake_type="New Inventory",
            intake_status="Pending",
            serial_no=self.serial_no.serial_no,
            manufacturer="Buffet",
            model="R13",
        )
        base.update(overrides)
        return frappe.get_doc(base).insert(ignore_permissions=True)

    # --------------------------------------------------------------------- #
    # Tests
    # --------------------------------------------------------------------- #

    def test_auto_creates_instrument_inspection(self):
        intake = self._make_intake()
        inspection = frappe.get_value(
            "Instrument Inspection",
            {"clarinet_intake": intake.name, "serial_no": self.serial_no.serial_no},
            ["name", "inspection_type"],
        )
        self.assertIsNotNone(inspection)
        self.assertEqual(inspection[1], "Initial Inspection")

    def test_no_duplicate_instrument_inspection(self):
        intake = self._make_intake()
        intake.manufacturer = "Yamaha"
        intake.save(ignore_permissions=True)
        inspections = frappe.get_all(
            "Instrument Inspection",
            filters={
                "clarinet_intake": intake.name,
                "serial_no": self.serial_no.serial_no,
            },
        )
        self.assertEqual(len(inspections), 1)

    def test_no_inspection_created_without_serial_no(self):
        intake = self._make_intake(serial_no=None)
        inspection = frappe.get_value("Instrument Inspection", {"clarinet_intake": intake.name})
        self.assertIsNone(inspection)
