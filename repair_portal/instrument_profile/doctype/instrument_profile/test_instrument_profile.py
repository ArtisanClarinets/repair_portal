# File: repair_portal/instrument_profile/doctype/instrument_profile/test_instrument_profile.py
# Created: 2025-06-13
# Version: 1.0
# Purpose: Unit test for Instrument Profile Doctype

import unittest

import frappe
import pytest


class TestInstrumentProfile(unittest.TestCase):
    def test_instrument_profile_creation(self):
        doc = frappe.get_doc(
            {
                'doctype': 'Instrument Profile',
                'instrument_type': 'Clarinet',
                'serial_number': 'TEST123',
                'acquisition_type': 'Inventory',
                'status': 'Active',
            }
        )
        doc.insert()
        assert doc.serial_number == 'TEST123'

    def test_customer_required_for_customer_type(self):
        doc = frappe.get_doc(
            {
                'doctype': 'Instrument Profile',
                'instrument_type': 'Clarinet',
                'serial_number': 'REQ-CUST-001',
                'acquisition_type': 'Customer',
                'status': 'Active',
            }
        )
        with pytest.raises(frappe.ValidationError):
            doc.insert()
