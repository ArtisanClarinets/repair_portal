"""
Test suite for Instrument Setup module.
Comprehensive testing covering all DocTypes, workflows, and edge cases.
"""

import contextlib
import unittest

import frappe
import pytest
from frappe.utils import add_days, nowdate


class TestInstrumentSetup(unittest.TestCase):
    """Main test class for instrument setup functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test data once for all tests."""
        frappe.set_user("Administrator")
        
        # Create test instrument and related data
        cls.test_instrument = frappe.get_doc({
            "doctype": "Instrument",
            "serial_no": "TEST-12345",
            "model": "Test Clarinet Model",
            "brand": "Test Brand",
        })
        if not frappe.db.exists("Instrument", cls.test_instrument.serial_no):
            cls.test_instrument.insert()

        # Create test setup template
        cls.test_template = frappe.get_doc({
            "doctype": "Setup Template",
            "template_name": "Test Standard Setup",
            "clarinet_model": "Test Clarinet Model",
            "setup_type": "Standard Setup",
            "priority": "Medium",
            "estimated_cost": 150.0,
            "estimated_materials_cost": 50.0,
            "estimated_hours": 2.0,
            "is_active": 1,
        })
        if not frappe.db.exists("Setup Template", cls.test_template.template_name):
            cls.test_template.insert()

    def setUp(self):
        """Set up for each test."""
        frappe.set_user("Administrator")

    def test_clarinet_initial_setup_creation(self):
        """Test creating a new clarinet initial setup."""
        setup = frappe.get_doc({
            "doctype": "Clarinet Initial Setup",
            "instrument": self.test_instrument.name,
            "setup_template": self.test_template.name,
            "setup_type": "Standard Setup",
            "priority": "Medium",
            "expected_start_date": nowdate(),
            "expected_end_date": add_days(nowdate(), 2),
        })
        
        setup.insert()
        assert setup.name
        assert setup.status == "Open"
        assert setup.setup_type == "Standard Setup"
        
        # Test defaults from template
        assert setup.estimated_cost == 150.0
        assert setup.estimated_materials_cost == 50.0
        
        return setup

    def test_setup_task_creation_and_dependencies(self):
        """Test setup task creation with dependencies."""
        setup = self.test_clarinet_initial_setup_creation()
        
        # Create parent task
        parent_task = frappe.get_doc({
            "doctype": "Clarinet Setup Task",
            "clarinet_initial_setup": setup.name,
            "subject": "Initial Inspection",
            "priority": "High",
            "sequence": 1,
            "exp_duration_mins": 30,
        })
        parent_task.insert()
        
        # Create dependent task
        dependent_task = frappe.get_doc({
            "doctype": "Clarinet Setup Task",
            "clarinet_initial_setup": setup.name,
            "subject": "Pad Adjustment",
            "priority": "Medium",
            "sequence": 2,
            "exp_duration_mins": 60,
            "depends_on": [{"task": parent_task.name}]
        })
        dependent_task.insert()
        
        # Test dependency validation
        dependent_task.status = "Working"
        with pytest.raises(frappe.ValidationError):
            dependent_task.save()
        
        # Complete parent task and test dependent can now start
        parent_task.status = "Completed"
        parent_task.save()
        
        dependent_task.reload()
        dependent_task.status = "Working"
        dependent_task.save()  # Should not raise error now

    def test_setup_template_operations_loading(self):
        """Test loading operations from setup template."""
        setup = self.test_clarinet_initial_setup_creation()
        
        # Add operations to template
        self.test_template.append("default_operations", {
            "operation_type": "Pad Leveling",
            "section": "All",
            "details": "Level all pads for proper sealing"
        })
        self.test_template.save()
        
        # Load operations from template
        setup.load_operations_from_template()
        
        assert len(setup.operations_performed) == 1
        assert setup.operations_performed[0].operation_type == "Pad Leveling"

    def test_clarinet_pad_map_creation(self):
        """Test clarinet pad map creation and pad entry handling."""
        pad_map = frappe.get_doc({
            "doctype": "Clarinet Pad Map",
            "clarinet_model": "Test Clarinet Model",
        })
        pad_map.insert()
        
        # Add pad entries
        pad_map.append("top_joint_pads", {
            "pad_position": "G#",
            "pad_size": "9.5mm",
            "material_type": "Leather",
            "is_open_key": 1
        })
        pad_map.append("bottom_joint_pads", {
            "pad_position": "Low E",
            "pad_size": "14mm", 
            "material_type": "Synthetic",
            "is_open_key": 0
        })
        pad_map.save()
        
        assert len(pad_map.top_joint_pads) == 1
        assert len(pad_map.bottom_joint_pads) == 1
        assert pad_map.top_joint_pads[0].is_open_key == 1

    def test_permission_enforcement(self):
        """Test permission enforcement on whitelisted methods."""
        frappe.set_user("test@example.com")  # Non-admin user
        
        setup = self.test_clarinet_initial_setup_creation()
        frappe.set_user("Administrator")  # Reset for setup creation
        
        # Test that non-admin cannot access certain methods
        frappe.set_user("test@example.com")
        
        with pytest.raises(frappe.PermissionError):
            setup.load_operations_from_template()

    def test_progress_calculation(self):
        """Test progress calculation across tasks."""
        setup = self.test_clarinet_initial_setup_creation()
        
        # Create multiple tasks
        tasks = []
        for i in range(3):
            task = frappe.get_doc({
                "doctype": "Clarinet Setup Task",
                "clarinet_initial_setup": setup.name,
                "subject": f"Task {i+1}",
                "priority": "Medium",
                "sequence": i+1,
                "progress": 0,
            })
            task.insert()
            tasks.append(task)
        
        # Complete tasks progressively
        tasks[0].progress = 100
        tasks[0].status = "Completed"
        tasks[0].save()
        
        tasks[1].progress = 50
        tasks[1].save()
        
        # Check parent progress calculation
        from repair_portal.repair_portal.instrument_setup.doctype.clarinet_setup_task.clarinet_setup_task import (
            update_parent_progress_inline,
        )
        update_parent_progress_inline(setup.name)
        
        setup.reload()
        expected_progress = (100 + 50 + 0) / 3
        assert setup.progress == round(expected_progress, 2)

    def test_data_validation(self):
        """Test data validation rules."""
        # Test date validation
        setup = frappe.get_doc({
            "doctype": "Clarinet Initial Setup",
            "instrument": self.test_instrument.name,
            "setup_template": self.test_template.name,
            "expected_start_date": add_days(nowdate(), 5),
            "expected_end_date": nowdate(),  # End before start
        })
        
        with pytest.raises(frappe.ValidationError):
            setup.insert()

    def test_certificate_generation(self):
        """Test setup certificate generation."""
        setup = self.test_clarinet_initial_setup_creation()
        setup.status = "Completed"
        setup.submit()
        
        # Check that certificate generation was attempted
        assert setup.status == "Completed"
        assert setup.actual_end_date

    def test_material_logging(self):
        """Test material usage logging."""
        setup = self.test_clarinet_initial_setup_creation()
        
        # Add material usage
        setup.append("materials_used", {
            "material_type": "Pad",
            "quantity": 5,
            "cost": 25.0,
            "notes": "Replacement pads for tone holes"
        })
        setup.save()
        
        assert len(setup.materials_used) == 1
        assert setup.materials_used[0].quantity == 5

    def tearDown(self):
        """Clean up after each test."""
        frappe.db.rollback()

    @classmethod
    def tearDownClass(cls):
        """Clean up test data after all tests."""
        frappe.set_user("Administrator")
        
        # Clean up test documents
        test_docs = [
            ("Clarinet Initial Setup", {"instrument": cls.test_instrument.name}),
            ("Clarinet Setup Task", {"clarinet_initial_setup": ["like", "%"]}),
            ("Setup Template", {"template_name": cls.test_template.template_name}),
            ("Instrument", {"serial_no": cls.test_instrument.serial_no}),
        ]
        
        for doctype, filters in test_docs:
            docs = frappe.get_all(doctype, filters=filters)
            for doc in docs:
                with contextlib.suppress(Exception):
                    frappe.delete_doc(doctype, doc.name, ignore_permissions=True)


def make_test_records_for_instrument_setup():
    """Create test records needed for instrument setup tests."""
    records = [
        # Instrument Category
        {
            "doctype": "Instrument Category",
            "title": "Woodwind",
            "description": "Woodwind instruments"
        },
        # Instrument Model
        {
            "doctype": "Instrument Model", 
            "model_name": "Test Clarinet Model",
            "instrument_category": "Woodwind",
            "brand": "Test Brand"
        }
    ]
    
    for record in records:
        if not frappe.db.exists(record["doctype"], record.get("title") or record.get("model_name")):
            frappe.get_doc(record).insert(ignore_permissions=True)


if __name__ == "__main__":
    make_test_records_for_instrument_setup()
    unittest.main()