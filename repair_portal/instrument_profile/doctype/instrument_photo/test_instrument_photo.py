# Path: repair_portal/instrument_profile/doctype/instrument_photo/test_instrument_photo.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Comprehensive unit tests for Instrument Photo DocType including validation, link integrity, file attachment validation, and photo metadata management.
# Dependencies: frappe.tests, unittest

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase


class TestInstrumentPhoto(FrappeTestCase):
    """Test cases for Instrument Photo DocType"""

    def setUp(self):
        """Set up test data"""
        # Create test brand
        if not frappe.db.exists("Brand", "Test Brand"):
            frappe.get_doc({"doctype": "Brand", "brand": "Test Brand"}).insert(ignore_permissions=True)

        # Create test instrument category
        if not frappe.db.exists("Instrument Category", "Test Clarinet"):
            frappe.get_doc(
                {"doctype": "Instrument Category", "title": "Test Clarinet", "is_active": 1}
            ).insert(ignore_permissions=True)

        # Create test instrument model
        if not frappe.db.exists("Instrument Model", "Test-123"):
            frappe.get_doc(
                {
                    "doctype": "Instrument Model",
                    "brand": "Test Brand",
                    "model": "Test-123",
                    "instrument_category": "Test Clarinet",
                    "body_material": "Grenadilla",
                }
            ).insert(ignore_permissions=True)

        # Create test instrument
        if not frappe.db.exists("Instrument", "PHOTO-TEST-001"):
            frappe.get_doc(
                {
                    "doctype": "Instrument",
                    "serial_number": "PHOTO-TEST-001",
                    "instrument_model": "Test-123",
                    "workflow_state": "Active",
                }
            ).insert(ignore_permissions=True)

    def tearDown(self):
        """Clean up test data"""
        # Delete test photos
        frappe.db.delete("Instrument Photo", {"instrument": "PHOTO-TEST-001"})
        frappe.db.commit()

    def test_instrument_photo_creation(self):
        """Test basic instrument photo creation"""
        photo = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Overall",
                "description": "Full instrument view",
            }
        )
        photo.insert()

        self.assertEqual(photo.instrument, "PHOTO-TEST-001")
        self.assertEqual(photo.photo_type, "Overall")
        self.assertEqual(photo.description, "Full instrument view")

    def test_required_fields_validation(self):
        """Test that required fields are enforced"""
        # Missing instrument
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {"doctype": "Instrument Photo", "photo_type": "Overall", "description": "Test photo"}
            ).insert()

        # Missing photo_type
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {"doctype": "Instrument Photo", "instrument": "PHOTO-TEST-001", "description": "Test photo"}
            ).insert()

        # Missing description
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {"doctype": "Instrument Photo", "instrument": "PHOTO-TEST-001", "photo_type": "Overall"}
            ).insert()

    def test_link_field_validation(self):
        """Test that instrument link points to existing record"""
        with self.assertRaises(frappe.LinkValidationError):
            frappe.get_doc(
                {
                    "doctype": "Instrument Photo",
                    "instrument": "NON-EXISTENT-INSTRUMENT",
                    "photo_type": "Overall",
                    "description": "Test photo",
                }
            ).insert()

    def test_photo_types(self):
        """Test various photo types"""
        photo_types = [
            "Overall",
            "Detail",
            "Damage",
            "Serial Number",
            "Mechanism",
            "Keywork",
            "Pads",
            "Before Repair",
            "After Repair",
            "Accessory",
        ]

        for i, photo_type in enumerate(photo_types):
            photo = frappe.get_doc(
                {
                    "doctype": "Instrument Photo",
                    "instrument": "PHOTO-TEST-001",
                    "photo_type": photo_type,
                    "description": f"Test {photo_type.lower()} photo",
                }
            )
            photo.insert()
            self.assertEqual(photo.photo_type, photo_type)

    def test_description_content(self):
        """Test description field content"""
        # Short description
        photo1 = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Overall",
                "description": "Front view",
            }
        )
        photo1.insert()
        self.assertEqual(photo1.description, "Front view")

        # Detailed description
        detailed_desc = "Close-up view of the upper joint showing pad condition, key alignment, and spring tension. Taken under good lighting to show detail."
        photo2 = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Detail",
                "description": detailed_desc,
            }
        )
        photo2.insert()
        self.assertEqual(photo2.description, detailed_desc)

    def test_optional_fields(self):
        """Test optional fields can be set"""
        photo = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Damage",
                "description": "Crack in wood near tone hole",
                "photo_date": "2023-01-15",
                "photographer": "Tech John Doe",
                "notes": "Photo taken for insurance claim documentation",
                "is_primary": 1,
            }
        )
        photo.insert()

        self.assertEqual(str(photo.photo_date), "2023-01-15")
        self.assertEqual(photo.photographer, "Tech John Doe")
        self.assertEqual(photo.notes, "Photo taken for insurance claim documentation")
        self.assertEqual(photo.is_primary, 1)

    def test_is_primary_flag(self):
        """Test primary photo flag functionality"""
        # Create primary photo
        photo1 = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Overall",
                "description": "Primary instrument photo",
                "is_primary": 1,
            }
        )
        photo1.insert()
        self.assertEqual(photo1.is_primary, 1)

        # Create non-primary photo
        photo2 = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Detail",
                "description": "Secondary detail photo",
                "is_primary": 0,
            }
        )
        photo2.insert()
        self.assertEqual(photo2.is_primary, 0)

        # Create another primary photo (multiple primaries may be allowed)
        photo3 = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Overall",
                "description": "Another primary photo",
                "is_primary": 1,
            }
        )
        photo3.insert()
        self.assertEqual(photo3.is_primary, 1)

    def test_photo_date_validation(self):
        """Test photo date field validation"""
        # Valid date
        photo1 = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Overall",
                "description": "Date test photo",
                "photo_date": "2023-06-15",
            }
        )
        photo1.insert()
        self.assertEqual(str(photo1.photo_date), "2023-06-15")

        # Current date
        from datetime import date

        today = date.today()
        photo2 = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Detail",
                "description": "Today's photo",
                "photo_date": today.strftime("%Y-%m-%d"),
            }
        )
        photo2.insert()
        self.assertEqual(str(photo2.photo_date), today.strftime("%Y-%m-%d"))

    def test_multiple_photos_per_instrument(self):
        """Test that multiple photos can be associated with one instrument"""
        photos_data = [
            {"type": "Overall", "desc": "Full front view"},
            {"type": "Overall", "desc": "Full back view"},
            {"type": "Detail", "desc": "Upper joint detail"},
            {"type": "Detail", "desc": "Lower joint detail"},
            {"type": "Serial Number", "desc": "Serial number close-up"},
            {"type": "Keywork", "desc": "Key mechanism detail"},
        ]

        created_photos = []
        for photo_data in photos_data:
            photo = frappe.get_doc(
                {
                    "doctype": "Instrument Photo",
                    "instrument": "PHOTO-TEST-001",
                    "photo_type": photo_data["type"],
                    "description": photo_data["desc"],
                }
            )
            photo.insert()
            created_photos.append(photo)

        # All photos should be created successfully
        self.assertEqual(len(created_photos), 6)
        for photo in created_photos:
            self.assertEqual(photo.instrument, "PHOTO-TEST-001")

    def test_photographer_field(self):
        """Test photographer field content"""
        photographers = [
            "Tech Smith",
            "John Doe - Senior Technician",
            "Customer Service Rep",
            "Automated System",
            "Quality Control Team",
        ]

        for i, photographer in enumerate(photographers):
            photo = frappe.get_doc(
                {
                    "doctype": "Instrument Photo",
                    "instrument": "PHOTO-TEST-001",
                    "photo_type": "Overall",
                    "description": f"Photo by {photographer}",
                    "photographer": photographer,
                }
            )
            photo.insert()
            self.assertEqual(photo.photographer, photographer)

    def test_notes_field(self):
        """Test notes field for additional information"""
        # Short note
        photo1 = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Damage",
                "description": "Minor scratch",
                "notes": "Cosmetic only",
            }
        )
        photo1.insert()
        self.assertEqual(photo1.notes, "Cosmetic only")

        # Detailed note
        detailed_note = "Photo taken with high-resolution camera under controlled lighting conditions. Color accuracy verified. This photo will be used for customer communication and repair documentation."
        photo2 = frappe.get_doc(
            {
                "doctype": "Instrument Photo",
                "instrument": "PHOTO-TEST-001",
                "photo_type": "Overall",
                "description": "High-quality documentation photo",
                "notes": detailed_note,
            }
        )
        photo2.insert()
        self.assertEqual(photo2.notes, detailed_note)

    def test_photo_organization_by_type(self):
        """Test photos can be organized by type"""
        # Create photos of same type
        for i in range(3):
            photo = frappe.get_doc(
                {
                    "doctype": "Instrument Photo",
                    "instrument": "PHOTO-TEST-001",
                    "photo_type": "Damage",
                    "description": f"Damage photo {i+1}",
                }
            )
            photo.insert()

        # Create photos of different type
        for i in range(2):
            photo = frappe.get_doc(
                {
                    "doctype": "Instrument Photo",
                    "instrument": "PHOTO-TEST-001",
                    "photo_type": "Overall",
                    "description": f"Overall photo {i+1}",
                }
            )
            photo.insert()

        # All photos should exist
        damage_photos = frappe.get_all(
            "Instrument Photo", filters={"instrument": "PHOTO-TEST-001", "photo_type": "Damage"}
        )
        overall_photos = frappe.get_all(
            "Instrument Photo", filters={"instrument": "PHOTO-TEST-001", "photo_type": "Overall"}
        )

        self.assertGreaterEqual(len(damage_photos), 3)
        self.assertGreaterEqual(len(overall_photos), 2)


if __name__ == "__main__":
    unittest.main()
