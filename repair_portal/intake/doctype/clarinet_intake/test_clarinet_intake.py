# Copyright (c) 2025, DT and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestClarinetIntake(FrappeTestCase):
    def setUp(self):
        # Create a test Serial No (since Instrument Inspection requires it)
        self.serial_no = frappe.get_doc(
            {
                "doctype": "Serial No",
                "serial_no": "TST-CLIN-0001",
                "item_code": "TST-ITEM",
                "status": "Active",
            }
        ).insert(ignore_permissions=True)

    def tearDown(self):
        # Clean up test records
        frappe.db.delete("Instrument Inspection", {"serial_no": self.serial_no.serial_no})
        frappe.delete_doc("Serial No", self.serial_no.name, force=1)
        frappe.db.commit()

    def test_auto_creates_instrument_inspection(self):
        """
        Should auto-create a linked Instrument Inspection on Clarinet Intake insert
        """
        intake = frappe.get_doc(
            {
                "doctype": "Clarinet Intake",
                "intake_type": "Inventory",
                "intake_status": "Pending",
                "serial_no": self.serial_no.serial_no,
                "brand": "Buffet",
                "model": "R13",
            }
        ).insert(ignore_permissions=True)
        inspection = frappe.get_value(
            "Instrument Inspection",
            {"clarinet_intake": intake.name, "serial_no": self.serial_no.serial_no},
            ["name", "inspection_type"],
        )
        self.assertIsNotNone(inspection, "Instrument Inspection should be created for Intake")
        self.assertEqual(inspection[1], "New Inventory")

    def test_no_duplicate_instrument_inspection(self):
        """
        Should not create a second Instrument Inspection on update
        """
        intake = frappe.get_doc(
            {
                "doctype": "Clarinet Intake",
                "intake_type": "Inventory",
                "intake_status": "Pending",
                "serial_no": self.serial_no.serial_no,
                "brand": "Buffet",
                "model": "R13",
            }
        ).insert(ignore_permissions=True)
        # Try to trigger save again
        intake.brand = "Yamaha"
        intake.save(ignore_permissions=True)
        inspections = frappe.get_all(
            "Instrument Inspection",
            filters={"clarinet_intake": intake.name, "serial_no": self.serial_no.serial_no},
        )
        self.assertEqual(len(inspections), 1)

    def test_no_inspection_created_without_serial_no(self):
        """
        Should NOT create Instrument Inspection if serial_no is missing
        """
        intake = frappe.get_doc(
            {
                "doctype": "Clarinet Intake",
                "intake_type": "Inventory",
                "intake_status": "Pending",
                # 'serial_no': intentionally omitted
                "brand": "Buffet",
                "model": "R13",
            }
        ).insert(ignore_permissions=True)
        inspection = frappe.get_value("Instrument Inspection", {"clarinet_intake": intake.name})
        self.assertIsNone(inspection)

    def test_blocked_edit_and_delete_when_flagged(self):
        """
        Editing and deleting should be blocked if intake_status == 'Flagged'
        """
        intake = frappe.get_doc(
            {
                "doctype": "Clarinet Intake",
                "intake_type": "Repair",
                "intake_status": "Flagged",
                "serial_no": self.serial_no.serial_no,
                "brand": "Buffet",
                "model": "RC",
            }
        ).insert(ignore_permissions=True)
        # Test edit
        intake.model = "E11"
        with self.assertRaises(frappe.ValidationError):
            intake.save(ignore_permissions=True)
        # Test delete
        with self.assertRaises(frappe.ValidationError):
            intake.delete()
