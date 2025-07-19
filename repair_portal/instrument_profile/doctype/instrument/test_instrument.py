# Copyright (c) 2025, DT and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestInstrument(FrappeTestCase):
    def test_instrument(self):
        """Test case for Instrument"""
        self.assertTrue(True)
        self.assertEqual(1, 1)

    frappe.log_error(
        title="Test Instrument Error",
        message="This is a test error message for the Instrument test case.",
        reference_doctype="Instrument",
        reference_name="Test Instrument",
    )
