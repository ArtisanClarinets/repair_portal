# Path: repair_portal/player_profile/doctype/player_equipment_preference/test_player_equipment_preference.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Comprehensive test suite for Player Equipment Preference child table
# Dependencies: frappe.tests, Player Profile, Player Equipment Preference

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPlayerEquipmentPreference(FrappeTestCase):
    """Test suite for Player Equipment Preference child table"""

    def setUp(self):
        """Set up test fixtures"""
        self.cleanup_test_data()

        # Create parent player profile
        self.player_profile = frappe.get_doc(
            {
                "doctype": "Player Profile",
                "player_name": "Equipment Test Player",
                "primary_email": "equipment.parent@example.com",
                "player_level": "Student (Advanced)",
            }
        )
        self.player_profile.insert()

    def tearDown(self):
        """Clean up after tests"""
        self.cleanup_test_data()

    def cleanup_test_data(self):
        """Remove test data"""
        profiles = frappe.get_all(
            "Player Profile",
            filters={"primary_email": ["like", "%equipment%@example.com%"]},
            pluck="name",
        )
        for profile in profiles:
            frappe.delete_doc("Player Profile", profile, force=True)
        frappe.db.commit()

    # === CREATION TESTS ===

    def test_add_equipment_preference_to_profile(self):
        """Test adding equipment preference to player profile"""
        self.player_profile.append(
            "equipment_preferences",
            {
                "mouthpiece": "Vandoren B45",
                "ligature": "Rovner Dark",
                "reed_brand": "Vandoren",
                "reed_model": "V12",
                "reed_strength": "3.5",
                "barrel": "Backun MoBa",
                "comments": "Prefers darker sound",
            },
        )
        self.player_profile.save()

        self.assertEqual(len(self.player_profile.equipment_preferences), 1)
        pref = self.player_profile.equipment_preferences[0]
        self.assertEqual(pref.mouthpiece, "Vandoren B45")
        self.assertEqual(pref.reed_strength, "3.5")

    def test_multiple_equipment_preferences(self):
        """Test adding multiple equipment preferences"""
        # Setup 1: Bb Clarinet
        self.player_profile.append(
            "equipment_preferences",
            {
                "mouthpiece": "Vandoren M30",
                "reed_brand": "Vandoren",
                "reed_model": "Traditional",
                "reed_strength": "3.0",
                "comments": "For Bb clarinet",
            },
        )

        # Setup 2: A Clarinet
        self.player_profile.append(
            "equipment_preferences",
            {
                "mouthpiece": "Vandoren M30Lyre",
                "reed_brand": "Vandoren",
                "reed_model": "V12",
                "reed_strength": "3.5",
                "comments": "For A clarinet",
            },
        )

        self.player_profile.save()
        self.assertEqual(len(self.player_profile.equipment_preferences), 2)

    # === VALIDATION TESTS ===

    def test_instrument_link_validation(self):
        """Test validation of linked instrument"""
        # Create test instrument profile
        # This requires Instrument Profile DocType to exist
        # Placeholder for future implementation when instrument integration is tested
        pass

    def test_reed_strength_format(self):
        """Test reed strength accepts various formats"""
        valid_strengths = ["2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0"]

        for strength in valid_strengths:
            self.player_profile.equipment_preferences = []
            self.player_profile.append(
                "equipment_preferences",
                {
                    "reed_brand": "Vandoren",
                    "reed_strength": strength,
                },
            )
            self.player_profile.save()
            self.assertEqual(self.player_profile.equipment_preferences[0].reed_strength, strength)

    # === BUSINESS LOGIC TESTS ===

    def test_parent_relationship(self):
        """Test parent-child relationship integrity"""
        self.player_profile.append(
            "equipment_preferences",
            {
                "mouthpiece": "Test Mouthpiece",
            },
        )
        self.player_profile.save()

        pref = self.player_profile.equipment_preferences[0]
        self.assertEqual(pref.parent, self.player_profile.name)
        self.assertEqual(pref.parenttype, "Player Profile")
        self.assertEqual(pref.parentfield, "equipment_preferences")

    def test_equipment_preference_ordering(self):
        """Test that equipment preferences maintain order (idx)"""
        for i in range(5):
            self.player_profile.append(
                "equipment_preferences",
                {
                    "mouthpiece": f"Mouthpiece {i}",
                    "comments": f"Setup {i}",
                },
            )
        self.player_profile.save()

        # Verify idx values are sequential
        for i, pref in enumerate(self.player_profile.equipment_preferences):
            self.assertEqual(pref.idx, i + 1)

    # === UPDATE TESTS ===

    def test_update_equipment_preference(self):
        """Test updating existing equipment preference"""
        self.player_profile.append(
            "equipment_preferences",
            {
                "mouthpiece": "Original Mouthpiece",
                "reed_brand": "Original Brand",
            },
        )
        self.player_profile.save()

        # Update
        self.player_profile.equipment_preferences[0].mouthpiece = "Updated Mouthpiece"
        self.player_profile.equipment_preferences[0].reed_brand = "Updated Brand"
        self.player_profile.save()

        # Verify
        self.player_profile.reload()
        self.assertEqual(self.player_profile.equipment_preferences[0].mouthpiece, "Updated Mouthpiece")
        self.assertEqual(self.player_profile.equipment_preferences[0].reed_brand, "Updated Brand")

    def test_delete_equipment_preference(self):
        """Test deleting equipment preference"""
        self.player_profile.append(
            "equipment_preferences",
            {
                "mouthpiece": "To Be Deleted",
            },
        )
        self.player_profile.save()
        initial_count = len(self.player_profile.equipment_preferences)

        # Delete
        self.player_profile.equipment_preferences = []
        self.player_profile.save()

        # Verify
        self.player_profile.reload()
        self.assertEqual(len(self.player_profile.equipment_preferences), 0)
        self.assertEqual(initial_count, 1)

    # === EDGE CASE TESTS ===

    def test_empty_equipment_preference(self):
        """Test adding equipment preference with no fields filled"""
        self.player_profile.append("equipment_preferences", {})
        self.player_profile.save()

        # Should save successfully with all None/empty values
        self.assertEqual(len(self.player_profile.equipment_preferences), 1)

    def test_special_characters_in_comments(self):
        """Test handling special characters in comments field"""
        special_text = "Likes 'warm' tone, prefers \"darker\" reeds & setup (2.5-3.0)"

        self.player_profile.append(
            "equipment_preferences",
            {
                "comments": special_text,
            },
        )
        self.player_profile.save()

        self.player_profile.reload()
        self.assertEqual(self.player_profile.equipment_preferences[0].comments, special_text)

    def test_long_comments_field(self):
        """Test handling very long text in comments"""
        long_comment = "This is a very detailed comment. " * 50

        self.player_profile.append(
            "equipment_preferences",
            {
                "comments": long_comment,
            },
        )
        self.player_profile.save()

        self.player_profile.reload()
        self.assertEqual(self.player_profile.equipment_preferences[0].comments, long_comment)

    # === INTEGRATION TESTS ===

    def test_equipment_preference_with_instrument_link(self):
        """Test equipment preference linked to specific instrument"""
        # This requires creating an Instrument Profile
        # Placeholder for future implementation
        pass

    # === DATA INTEGRITY TESTS ===

    def test_cascade_delete_with_parent(self):
        """Test that child records are deleted when parent is deleted"""
        self.player_profile.append(
            "equipment_preferences",
            {
                "mouthpiece": "Test Cascade",
            },
        )
        self.player_profile.save()

        profile_name = self.player_profile.name

        # Delete parent
        frappe.delete_doc("Player Profile", profile_name, force=True)

        # Verify child records are also deleted
        children = frappe.get_all("Player Equipment Preference", filters={"parent": profile_name})
        self.assertEqual(len(children), 0)
