# Path: repair_portal/instrument_profile/doctype/instrument_serial_number/test_instrument_serial_number.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Comprehensive tests for Instrument Serial Number: normalization, duplicate detection, verification, linkage
# Dependencies: frappe.tests, repair_portal.utils.serials

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.utils.serials import ensure_instrument_serial, find_by_serial, normalize_serial


class TestInstrumentSerialNumber(FrappeTestCase):
    """Test Instrument Serial Number DocType"""

    def setUp(self):
        """Set up test fixtures"""
        # Create test instrument
        if not frappe.db.exists("Brand", "Test ISN Brand"):
            frappe.get_doc({"doctype": "Brand", "brand": "Test ISN Brand"}).insert(ignore_permissions=True)

        self.test_instrument = frappe.get_doc(
            {
                "doctype": "Instrument",
                "serial_no": f"TESTISN-{frappe.generate_hash(length=6)}",
                "brand": "Test ISN Brand",
                "clarinet_type": "Bb Clarinet",
                "current_status": "Active",
            }
        )
        self.test_instrument.insert(ignore_permissions=True)

    def tearDown(self):
        """Clean up test data"""
        # Delete test instrument
        if hasattr(self, "test_instrument"):
            frappe.delete_doc("Instrument", self.test_instrument.name, force=True, ignore_permissions=True)

        # Delete any test ISNs
        test_isns = frappe.get_all(
            "Instrument Serial Number", filters={"serial": ["like", "TEST-%"]}, pluck="name"
        )
        for isn in test_isns:
            frappe.delete_doc("Instrument Serial Number", isn, force=True, ignore_permissions=True)

    def test_normalization(self):
        """Test serial number normalization"""
        test_cases = [
            ("A-123 456", "A123456"),
            ("a-123-456", "A123456"),
            ("  A 123  ", "A123"),
            ("X.Y.Z.789", "XYZ789"),
            ("123ABC", "123ABC"),
        ]

        for input_serial, expected_normalized in test_cases:
            result = normalize_serial(input_serial)
            self.assertEqual(result, expected_normalized, f"Failed for {input_serial}")

    def test_create_isn_with_normalization(self):
        """Test creating ISN with auto-normalization"""
        isn = frappe.get_doc(
            {
                "doctype": "Instrument Serial Number",
                "serial": "TEST-A-123",
                "serial_source": "Stamped",
                "instrument": self.test_instrument.name,
            }
        )
        isn.insert(ignore_permissions=True)

        self.assertEqual(isn.serial, "TEST-A-123")
        self.assertEqual(isn.normalized_serial, "TESTA123")

        frappe.delete_doc("Instrument Serial Number", isn.name, force=True, ignore_permissions=True)

    def test_duplicate_detection_same_instrument(self):
        """Test that duplicate ISN for same instrument is blocked"""
        isn1 = frappe.get_doc(
            {
                "doctype": "Instrument Serial Number",
                "serial": "TEST-DUP-001",
                "instrument": self.test_instrument.name,
            }
        )
        isn1.insert(ignore_permissions=True)

        # Try to create duplicate for same instrument
        isn2 = frappe.get_doc(
            {
                "doctype": "Instrument Serial Number",
                "serial": "TEST-DUP-001",  # Same serial
                "instrument": self.test_instrument.name,
            }
        )

        with self.assertRaises(frappe.ValidationError):
            isn2.insert(ignore_permissions=True)

        frappe.delete_doc("Instrument Serial Number", isn1.name, force=True, ignore_permissions=True)

    def test_verification_status_workflow(self):
        """Test verification status and auto-set fields"""
        isn = frappe.get_doc(
            {
                "doctype": "Instrument Serial Number",
                "serial": "TEST-VER-001",
                "verification_status": "Unverified",
                "instrument": self.test_instrument.name,
            }
        )
        isn.insert(ignore_permissions=True)

        self.assertEqual(isn.verification_status, "Unverified")
        self.assertFalse(isn.verified_by)

        # Verify as technician
        isn.verification_status = "Verified by Technician"
        isn.save(ignore_permissions=True)
        isn.reload()

        self.assertEqual(isn.verification_status, "Verified by Technician")
        self.assertTrue(isn.verified_by)
        self.assertTrue(isn.verified_on)

        frappe.delete_doc("Instrument Serial Number", isn.name, force=True, ignore_permissions=True)

    def test_find_by_serial(self):
        """Test find_by_serial utility function"""
        isn = frappe.get_doc(
            {
                "doctype": "Instrument Serial Number",
                "serial": "TEST-FIND-001",
                "instrument": self.test_instrument.name,
            }
        )
        isn.insert(ignore_permissions=True)

        # Find by exact serial
        found = find_by_serial("TEST-FIND-001")
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], isn.name)

        # Find by normalized form (case-insensitive)
        found2 = find_by_serial("test-find-001")
        self.assertIsNotNone(found2)
        self.assertEqual(found2["name"], isn.name)

        # Find with punctuation differences
        found3 = find_by_serial("TEST FIND 001")
        self.assertIsNotNone(found3)
        self.assertEqual(found3["name"], isn.name)

        frappe.delete_doc("Instrument Serial Number", isn.name, force=True, ignore_permissions=True)

    def test_ensure_instrument_serial_idempotent(self):
        """Test ensure_instrument_serial is idempotent"""
        # First call creates
        isn1_name = ensure_instrument_serial(
            serial_input="TEST-EIS-001", instrument=self.test_instrument.name, status="Active"
        )
        self.assertTrue(isn1_name)

        # Second call returns existing
        isn2_name = ensure_instrument_serial(
            serial_input="TEST-EIS-001", instrument=self.test_instrument.name, status="Active"
        )
        self.assertEqual(isn1_name, isn2_name)

        # Third call with different case/punctuation still returns same
        isn3_name = ensure_instrument_serial(
            serial_input="test eis 001", instrument=self.test_instrument.name
        )
        self.assertEqual(isn1_name, isn3_name)

        frappe.delete_doc("Instrument Serial Number", isn1_name, force=True, ignore_permissions=True)

    def test_scan_code_unique(self):
        """Test scan code functionality"""
        isn1 = frappe.get_doc(
            {
                "doctype": "Instrument Serial Number",
                "serial": "TEST-SCAN-001",
                "scan_code": "QR-TEST-001",
                "instrument": self.test_instrument.name,
            }
        )
        isn1.insert(ignore_permissions=True)

        # Verify scan code is saved
        self.assertEqual(isn1.scan_code, "QR-TEST-001")

        # Could test find_by_scan_code here
        from repair_portal.utils.serials import find_by_scan_code

        found = find_by_scan_code("QR-TEST-001")
        self.assertIsNotNone(found)

        frappe.delete_doc("Instrument Serial Number", isn1.name, force=True, ignore_permissions=True)

    def test_status_field(self):
        """Test status field values"""
        valid_statuses = ["Active", "Deprecated", "Replaced", "Error"]

        for status in valid_statuses:
            isn = frappe.get_doc(
                {
                    "doctype": "Instrument Serial Number",
                    "serial": f"TEST-STATUS-{status}",
                    "status": status,
                    "instrument": self.test_instrument.name,
                }
            )
            isn.insert(ignore_permissions=True)
            self.assertEqual(isn.status, status)
            frappe.delete_doc("Instrument Serial Number", isn.name, force=True, ignore_permissions=True)

    def test_duplicate_of_field(self):
        """Test duplicate_of linkage"""
        # Create primary ISN
        primary = frappe.get_doc(
            {
                "doctype": "Instrument Serial Number",
                "serial": "TEST-PRIMARY-001",
                "instrument": self.test_instrument.name,
                "status": "Active",
            }
        )
        primary.insert(ignore_permissions=True)

        # Create duplicate ISN pointing to primary
        duplicate = frappe.get_doc(
            {
                "doctype": "Instrument Serial Number",
                "serial": "TEST-DUP-ALT-001",  # Different serial to avoid uniqueness error
                "duplicate_of": primary.name,
                "status": "Deprecated",
            }
        )
        duplicate.insert(ignore_permissions=True)

        self.assertEqual(duplicate.duplicate_of, primary.name)

        frappe.delete_doc("Instrument Serial Number", duplicate.name, force=True, ignore_permissions=True)
        frappe.delete_doc("Instrument Serial Number", primary.name, force=True, ignore_permissions=True)

    def test_photo_attachment(self):
        """Test photo field stores attachment"""
        isn = frappe.get_doc(
            {
                "doctype": "Instrument Serial Number",
                "serial": "TEST-PHOTO-001",
                "instrument": self.test_instrument.name,
                "photo": "/files/test_serial_photo.jpg",  # Mock file path
            }
        )
        isn.insert(ignore_permissions=True)

        self.assertEqual(isn.photo, "/files/test_serial_photo.jpg")

        frappe.delete_doc("Instrument Serial Number", isn.name, force=True, ignore_permissions=True)


def run_all_tests():
    """Helper to run all ISN tests"""
    import unittest

    suite = unittest.TestLoader().loadTestsFromTestCase(TestInstrumentSerialNumber)
    unittest.TextTestRunner(verbosity=2).run(suite)
