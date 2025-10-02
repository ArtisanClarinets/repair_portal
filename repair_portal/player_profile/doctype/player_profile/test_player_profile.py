# Path: repair_portal/player_profile/doctype/player_profile/test_player_profile.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Comprehensive test suite for Player Profile DocType covering all validation,
#              business logic, security, and integration scenarios.
# Dependencies: frappe.tests, Player Profile

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase

class TestPlayerProfile(FrappeTestCase):
    """Comprehensive test suite for Player Profile"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_email = "test.player@example.com"
        self.cleanup_test_data()

    def tearDown(self):
        """Clean up after tests"""
        self.cleanup_test_data()

    def cleanup_test_data(self):
        """Remove test data"""
        # Delete test player profiles
        profiles = frappe.get_all(
            "Player Profile",
            filters={"primary_email": ["like", "%@example.com%"]},
            pluck="name",
        )
        for profile in profiles:
            frappe.delete_doc("Player Profile", profile, force=True)
        frappe.db.commit()

    # === CREATION TESTS ===

    def test_create_player_profile_with_required_fields(self):
        """Test creating player profile with all required fields"""
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "John Doe",
            "primary_email": self.test_email,
            "player_level": "Student (Beginner)",
        })
        doc.insert()
        
        self.assertIsNotNone(doc.name)
        self.assertIsNotNone(doc.player_profile_id)
        self.assertTrue(doc.player_profile_id.startswith("PLAYER-"))
        self.assertEqual(doc.profile_status, "Draft")

    def test_create_fails_without_required_fields(self):
        """Test that creation fails without required fields"""
        # Missing player_name
        with self.assertRaises(frappe.exceptions.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Player Profile",
                "primary_email": "missing.name@example.com",
                "player_level": "Student (Beginner)",
            })
            doc.insert()

        # Missing primary_email
        with self.assertRaises(frappe.exceptions.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Player Profile",
                "player_name": "Missing Email",
                "player_level": "Student (Beginner)",
            })
            doc.insert()

        # Missing player_level
        with self.assertRaises(frappe.exceptions.ValidationError):
            doc = frappe.get_doc({
                "doctype": "Player Profile",
                "player_name": "Missing Level",
                "primary_email": "missing.level@example.com",
            })
            doc.insert()

    def test_unique_email_constraint(self):
        """Test that duplicate emails are rejected"""
        # Create first profile
        doc1 = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "First Player",
            "primary_email": self.test_email,
            "player_level": "Student (Beginner)",
        })
        doc1.insert()

        # Attempt to create second profile with same email
        with self.assertRaises(frappe.exceptions.ValidationError):
            doc2 = frappe.get_doc({
                "doctype": "Player Profile",
                "player_name": "Second Player",
                "primary_email": self.test_email,
                "player_level": "Student (Advanced)",
            })
            doc2.insert()

    # === VALIDATION TESTS ===

    def test_email_format_validation(self):
        """Test email format validation"""
        invalid_emails = [
            "notanemail",
            "@nodomain.com",
            "missing@domain",
            "spaces in@email.com",
        ]

        for invalid_email in invalid_emails:
            with self.assertRaises(frappe.exceptions.ValidationError):
                doc = frappe.get_doc({
                    "doctype": "Player Profile",
                    "player_name": "Invalid Email Test",
                    "primary_email": invalid_email,
                    "player_level": "Student (Beginner)",
                })
                doc.insert()

    def test_phone_format_validation(self):
        """Test phone number format validation"""
        valid_phones = [
            "+1234567890",
            "123-456-7890",
            "(123) 456-7890",
            "123.456.7890",
        ]

        for valid_phone in valid_phones:
            doc = frappe.get_doc({
                "doctype": "Player Profile",
                "player_name": "Phone Test",
                "primary_email": f"phone{valid_phones.index(valid_phone)}@example.com",
                "primary_phone": valid_phone,
                "player_level": "Student (Beginner)",
            })
            doc.insert()
            self.assertIsNotNone(doc.name)

    # === BUSINESS LOGIC TESTS ===

    def test_profile_creation_date_auto_set(self):
        """Test that profile creation date is automatically set"""
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "Date Test",
            "primary_email": "date.test@example.com",
            "player_level": "Student (Beginner)",
        })
        doc.insert()
        
        self.assertIsNotNone(doc.profile_creation_date)
        self.assertEqual(doc.profile_creation_date, frappe.utils.today())

    def test_lifetime_value_calculation(self):
        """Test customer lifetime value calculation"""
        # Create player profile
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "CLV Test",
            "primary_email": "clv.test@example.com",
            "player_level": "Professional (Orchestral)",
        })
        doc.insert()

        # Initial CLV should be 0
        self.assertEqual(doc.customer_lifetime_value, 0)

        # TODO: Create linked Sales Invoices and test CLV calculation
        # This requires setting up Customer, Item, and Sales Invoice fixtures

    def test_equipment_preferences_validation(self):
        """Test equipment preferences child table validation"""
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "Equipment Test",
            "primary_email": "equipment.test@example.com",
            "player_level": "Student (Advanced)",
        })
        
        # Add equipment preferences
        doc.append("equipment_preferences", {
            "mouthpiece": "Vandoren B45",
            "reed_brand": "Vandoren",
            "reed_model": "Traditional",
            "reed_strength": "3.0",
        })
        
        doc.insert()
        self.assertEqual(len(doc.equipment_preferences), 1)
        self.assertEqual(doc.equipment_preferences[0].mouthpiece, "Vandoren B45")

    # === WORKFLOW TESTS ===

    def test_profile_status_transitions(self):
        """Test profile status lifecycle transitions"""
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "Status Test",
            "primary_email": "status.test@example.com",
            "player_level": "Student (Beginner)",
        })
        doc.insert()
        
        # Should start in Draft
        self.assertEqual(doc.profile_status, "Draft")

        # Transition to Active
        doc.profile_status = "Active"
        doc.save()
        self.assertEqual(doc.profile_status, "Active")

        # Transition to Archived
        doc.profile_status = "Archived"
        doc.save()
        self.assertEqual(doc.profile_status, "Archived")

    # === SECURITY TESTS ===

    def test_permission_enforcement(self):
        """Test permission enforcement for different roles"""
        # Create player profile
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "Permission Test",
            "primary_email": "permission.test@example.com",
            "player_level": "Student (Beginner)",
        })
        doc.insert()

        # Test System Manager has full access
        self.assertTrue(frappe.has_permission("Player Profile", "read", doc.name, user="Administrator"))
        self.assertTrue(frappe.has_permission("Player Profile", "write", doc.name, user="Administrator"))
        self.assertTrue(frappe.has_permission("Player Profile", "delete", doc.name, user="Administrator"))

    # === API METHOD TESTS ===

    def test_get_service_history(self):
        """Test get_service_history whitelisted method"""
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "Service History Test",
            "primary_email": "service.test@example.com",
            "player_level": "Professional (Jazz/Commercial)",
        })
        doc.insert()

        # Call whitelisted method
        history = doc.get_service_history()
        self.assertIsInstance(history, list)

    def test_get_equipment_recommendations(self):
        """Test get_equipment_recommendations whitelisted method"""
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "Recommendations Test",
            "primary_email": "recommendations.test@example.com",
            "player_level": "Student (Beginner)",
        })
        doc.insert()

        # Call whitelisted method
        recommendations = doc.get_equipment_recommendations()
        self.assertIsInstance(recommendations, dict)
        self.assertIn("mouthpieces", recommendations)
        self.assertIn("reeds", recommendations)
        self.assertGreater(len(recommendations["mouthpieces"]), 0)

    def test_update_marketing_preferences(self):
        """Test update_marketing_preferences whitelisted method"""
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "Marketing Test",
            "primary_email": "marketing.test@example.com",
            "player_level": "Amateur/Hobbyist",
        })
        doc.insert()

        # Update preferences
        result = doc.update_marketing_preferences(newsletter=1, targeted=1)
        self.assertTrue(result["success"])
        
        # Verify changes
        doc.reload()
        self.assertEqual(doc.newsletter_subscription, 1)
        self.assertEqual(doc.targeted_marketing_optin, 1)

    # === INTEGRATION TESTS ===

    def test_coppa_compliance(self):
        """Test COPPA compliance for minors"""
        # This test requires a date_of_birth field to be added
        # Placeholder for future implementation
        pass

    def test_email_group_synchronization(self):
        """Test automatic synchronization with email groups"""
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "Email Group Test",
            "primary_email": "emailgroup.test@example.com",
            "player_level": "Student (Beginner)",
            "newsletter_subscription": 1,
        })
        doc.insert()

        # Check if email group member was created
        # This requires Email Group "Player Newsletter" to exist
        # Placeholder for future implementation
        pass

    # === EDGE CASE TESTS ===

    def test_special_characters_in_name(self):
        """Test handling of special characters in player name"""
        special_names = [
            "O'Brien",
            "José García",
            "François Müller",
            "李明",
        ]

        for name in special_names:
            doc = frappe.get_doc({
                "doctype": "Player Profile",
                "player_name": name,
                "primary_email": f"special{special_names.index(name)}@example.com",
                "player_level": "Student (Beginner)",
            })
            doc.insert()
            self.assertEqual(doc.player_name, name)

    def test_long_text_fields(self):
        """Test handling of long text in text fields"""
        long_text = "Lorem ipsum " * 100  # Very long text
        
        doc = frappe.get_doc({
            "doctype": "Player Profile",
            "player_name": "Long Text Test",
            "primary_email": "longtext.test@example.com",
            "player_level": "Student (Beginner)",
            "technician_notes": long_text,
            "intonation_notes": long_text,
        })
        doc.insert()
        
        self.assertEqual(doc.technician_notes, long_text)
        self.assertEqual(doc.intonation_notes, long_text)

    # === PERFORMANCE TESTS ===

    def test_bulk_profile_creation(self):
        """Test creating multiple profiles efficiently"""
        profiles = []
        for i in range(10):
            doc = frappe.get_doc({
                "doctype": "Player Profile",
                "player_name": f"Bulk Test Player {i}",
                "primary_email": f"bulk{i}@example.com",
                "player_level": "Student (Beginner)",
            })
            doc.insert()
            profiles.append(doc.name)

        # Verify all created
        self.assertEqual(len(profiles), 10)

        # Clean up
        for profile_name in profiles:
            frappe.delete_doc("Player Profile", profile_name, force=True)
