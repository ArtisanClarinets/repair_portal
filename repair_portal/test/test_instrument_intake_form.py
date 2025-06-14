import frappe
import unittest


class TestInstrumentIntakeForm(unittest.TestCase):
    def test_intake_creation(self):
        doc = frappe.get_doc(
            {
                'doctype': 'Instrument Intake Form',
                'customer': 'Test Customer',
                'instrument': 'Test Instrument',
                'repair_type': 'Basic',
                'terms_accepted': 1,
                'signature': '/files/test_signature.png',
            }
        )
        doc.insert()
        self.assertTrue(doc.name.startswith('INTAKE-'))
