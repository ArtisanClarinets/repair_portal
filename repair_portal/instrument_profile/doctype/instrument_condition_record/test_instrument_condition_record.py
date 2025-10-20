# Path: repair_portal/instrument_profile/doctype/instrument_condition_record/test_instrument_condition_record.py
# Date: 2025-10-02
# Version: 1.0.0
# Description: Comprehensive unit tests for Instrument Condition Record DocType including validation, link integrity, assessment scoring, condition tracking over time, and technician records.
# Dependencies: frappe.tests, unittest

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase


class TestInstrumentConditionRecord(FrappeTestCase):
    """Test cases for Instrument Condition Record DocType"""

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
        if not frappe.db.exists("Instrument", "COND-TEST-001"):
            frappe.get_doc(
                {
                    "doctype": "Instrument",
                    "serial_number": "COND-TEST-001",
                    "instrument_model": "Test-123",
                    "workflow_state": "Active",
                }
            ).insert(ignore_permissions=True)

    def tearDown(self):
        """Clean up test data"""
        # Delete test condition records
        frappe.db.delete("Instrument Condition Record", {"instrument": "COND-TEST-001"})
        frappe.db.commit()

    def test_condition_record_creation(self):
        """Test basic condition record creation"""
        record = frappe.get_doc(
            {
                "doctype": "Instrument Condition Record",
                "instrument": "COND-TEST-001",
                "assessment_date": "2023-01-15",
                "overall_condition": "Good",
                "condition_notes": "General wear but functional",
            }
        )
        record.insert()

        self.assertEqual(record.instrument, "COND-TEST-001")
        self.assertEqual(str(record.assessment_date), "2023-01-15")
        self.assertEqual(record.overall_condition, "Good")
        self.assertEqual(record.condition_notes, "General wear but functional")

    def test_required_fields_validation(self):
        """Test that required fields are enforced"""
        # Missing instrument
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {
                    "doctype": "Instrument Condition Record",
                    "assessment_date": "2023-01-15",
                    "overall_condition": "Good",
                    "condition_notes": "Test record",
                }
            ).insert()

        # Missing assessment_date
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {
                    "doctype": "Instrument Condition Record",
                    "instrument": "COND-TEST-001",
                    "overall_condition": "Good",
                    "condition_notes": "Test record",
                }
            ).insert()

        # Missing overall_condition
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {
                    "doctype": "Instrument Condition Record",
                    "instrument": "COND-TEST-001",
                    "assessment_date": "2023-01-15",
                    "condition_notes": "Test record",
                }
            ).insert()

    def test_link_field_validation(self):
        """Test that instrument link points to existing record"""
        with self.assertRaises(frappe.LinkValidationError):
            frappe.get_doc(
                {
                    "doctype": "Instrument Condition Record",
                    "instrument": "NON-EXISTENT-INSTRUMENT",
                    "assessment_date": "2023-01-15",
                    "overall_condition": "Good",
                    "condition_notes": "Test record",
                }
            ).insert()

    def test_overall_condition_values(self):
        """Test valid overall condition values"""
        conditions = ["Excellent", "Good", "Fair", "Poor", "Needs Repair", "Not Functional"]

        for i, condition in enumerate(conditions):
            record = frappe.get_doc(
                {
                    "doctype": "Instrument Condition Record",
                    "instrument": "COND-TEST-001",
                    "assessment_date": f"2023-01-{str(i+10).zfill(2)}",
                    "overall_condition": condition,
                    "condition_notes": f"Assessment with {condition.lower()} condition",
                }
            )
            record.insert()
            self.assertEqual(record.overall_condition, condition)

    def test_assessment_date_validation(self):
        """Test assessment date field validation"""
        # Valid past date
        record1 = frappe.get_doc(
            {
                "doctype": "Instrument Condition Record",
                "instrument": "COND-TEST-001",
                "assessment_date": "2023-06-15",
                "overall_condition": "Good",
                "condition_notes": "Past assessment",
            }
        )
        record1.insert()
        self.assertEqual(str(record1.assessment_date), "2023-06-15")

        # Current date
        from datetime import date

        today = date.today()
        record2 = frappe.get_doc(
            {
                "doctype": "Instrument Condition Record",
                "instrument": "COND-TEST-001",
                "assessment_date": today.strftime("%Y-%m-%d"),
                "overall_condition": "Good",
                "condition_notes": "Current assessment",
            }
        )
        record2.insert()
        self.assertEqual(str(record2.assessment_date), today.strftime("%Y-%m-%d"))

    def test_condition_notes_content(self):
        """Test condition notes field content"""
        # Short note
        record1 = frappe.get_doc(
            {
                "doctype": "Instrument Condition Record",
                "instrument": "COND-TEST-001",
                "assessment_date": "2023-02-01",
                "overall_condition": "Good",
                "condition_notes": "Plays well",
            }
        )
        record1.insert()
        self.assertEqual(record1.condition_notes, "Plays well")

        # Detailed assessment
        detailed_notes = "Instrument shows normal wear for age. Pads are in good condition with proper sealing. Keys are aligned and springs have good tension. Minor cosmetic scratches on body but no impact on playability. Recommended for continued use with routine maintenance."
        record2 = frappe.get_doc(
            {
                "doctype": "Instrument Condition Record",
                "instrument": "COND-TEST-001",
                "assessment_date": "2023-02-02",
                "overall_condition": "Good",
                "condition_notes": detailed_notes,
            }
        )
        record2.insert()
        self.assertEqual(record2.condition_notes, detailed_notes)

    def test_optional_fields(self):
        """Test optional fields can be set"""
        record = frappe.get_doc(
            {
                "doctype": "Instrument Condition Record",
                "instrument": "COND-TEST-001",
                "assessment_date": "2023-03-01",
                "overall_condition": "Fair",
                "condition_notes": "Needs some attention",
                "assessed_by": "Tech John Smith",
                "pad_condition": "Good",
                "spring_condition": "Fair",
                "key_alignment": "Good",
                "intonation_quality": "Excellent",
                "playability_score": 7,
                "recommended_action": "Schedule maintenance",
                "next_assessment_date": "2023-09-01",
            }
        )
        record.insert()

        self.assertEqual(record.assessed_by, "Tech John Smith")
        self.assertEqual(record.pad_condition, "Good")
        self.assertEqual(record.spring_condition, "Fair")
        self.assertEqual(record.key_alignment, "Good")
        self.assertEqual(record.intonation_quality, "Excellent")
        self.assertEqual(record.playability_score, 7)
        self.assertEqual(record.recommended_action, "Schedule maintenance")
        self.assertEqual(str(record.next_assessment_date), "2023-09-01")

    def test_component_condition_values(self):
        """Test individual component condition values"""
        components = ["pad_condition", "spring_condition", "key_alignment", "intonation_quality"]
        conditions = ["Excellent", "Good", "Fair", "Poor", "Needs Replacement"]

        for i, condition in enumerate(conditions):
            record_data = {
                "doctype": "Instrument Condition Record",
                "instrument": "COND-TEST-001",
                "assessment_date": f"2023-03-{str(i+10).zfill(2)}",
                "overall_condition": "Fair",
                "condition_notes": f"Testing {condition} component conditions",
            }

            # Set all components to the same condition
            for component in components:
                record_data[component] = condition

            record = frappe.get_doc(record_data)
            record.insert()

            for component in components:
                self.assertEqual(record.get(component), condition)

    def test_playability_score_validation(self):
        """Test playability score range validation"""
        # Valid scores (assuming 1-10 scale)
        valid_scores = [1, 3, 5, 7, 8, 10]

        for i, score in enumerate(valid_scores):
            record = frappe.get_doc(
                {
                    "doctype": "Instrument Condition Record",
                    "instrument": "COND-TEST-001",
                    "assessment_date": f"2023-04-{str(i+10).zfill(2)}",
                    "overall_condition": "Good",
                    "condition_notes": f"Score test with {score}",
                    "playability_score": score,
                }
            )
            record.insert()
            self.assertEqual(record.playability_score, score)

    def test_recommended_actions(self):
        """Test various recommended action values"""
        actions = [
            "No action needed",
            "Schedule routine maintenance",
            "Replace pads",
            "Adjust springs",
            "Professional overhaul required",
            "Consider replacement",
            "Immediate repair needed",
        ]

        for i, action in enumerate(actions):
            record = frappe.get_doc(
                {
                    "doctype": "Instrument Condition Record",
                    "instrument": "COND-TEST-001",
                    "assessment_date": f"2023-05-{str(i+10).zfill(2)}",
                    "overall_condition": "Fair",
                    "condition_notes": f"Testing action: {action}",
                    "recommended_action": action,
                }
            )
            record.insert()
            self.assertEqual(record.recommended_action, action)

    def test_multiple_assessments_timeline(self):
        """Test multiple assessments over time for same instrument"""
        assessments = [
            {"date": "2023-01-01", "condition": "Excellent", "notes": "New instrument assessment"},
            {"date": "2023-04-01", "condition": "Good", "notes": "Quarterly check - slight wear"},
            {"date": "2023-07-01", "condition": "Good", "notes": "Mid-year assessment - stable condition"},
            {"date": "2023-10-01", "condition": "Fair", "notes": "Annual assessment - needs attention"},
            {"date": "2024-01-01", "condition": "Good", "notes": "Post-maintenance assessment"},
        ]

        created_records = []
        for assessment in assessments:
            record = frappe.get_doc(
                {
                    "doctype": "Instrument Condition Record",
                    "instrument": "COND-TEST-001",
                    "assessment_date": assessment["date"],
                    "overall_condition": assessment["condition"],
                    "condition_notes": assessment["notes"],
                }
            )
            record.insert()
            created_records.append(record)

        # All assessments should be created
        self.assertEqual(len(created_records), 5)

        # Verify chronological order is maintained
        for i, record in enumerate(created_records):
            self.assertEqual(str(record.assessment_date), assessments[i]["date"])
            self.assertEqual(record.overall_condition, assessments[i]["condition"])

    def test_assessor_tracking(self):
        """Test tracking who performed assessments"""
        assessors = [
            "Senior Tech Alice Johnson",
            "Tech Bob Wilson",
            "QC Inspector Carol Davis",
            "Apprentice Dave Miller",
            "External Inspector Eve Thompson",
        ]

        for i, assessor in enumerate(assessors):
            record = frappe.get_doc(
                {
                    "doctype": "Instrument Condition Record",
                    "instrument": "COND-TEST-001",
                    "assessment_date": f"2023-06-{str(i+10).zfill(2)}",
                    "overall_condition": "Good",
                    "condition_notes": f"Assessment by {assessor}",
                    "assessed_by": assessor,
                }
            )
            record.insert()
            self.assertEqual(record.assessed_by, assessor)

    def test_next_assessment_scheduling(self):
        """Test next assessment date functionality"""
        record = frappe.get_doc(
            {
                "doctype": "Instrument Condition Record",
                "instrument": "COND-TEST-001",
                "assessment_date": "2023-06-01",
                "overall_condition": "Good",
                "condition_notes": "Scheduled next assessment",
                "next_assessment_date": "2023-12-01",
            }
        )
        record.insert()

        self.assertEqual(str(record.assessment_date), "2023-06-01")
        self.assertEqual(str(record.next_assessment_date), "2023-12-01")

        # Next assessment should be after current assessment
        self.assertGreater(record.next_assessment_date, record.assessment_date)


if __name__ == "__main__":
    unittest.main()
