"""Tests for Loaner Agreement DocType."""

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate


class TestLoanerAgreement(FrappeTestCase):
    """Validate loaner agreement workflow."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.instrument = cls._ensure_instrument()
        cls.loaner = cls._ensure_loaner(cls.instrument)

    @classmethod
    def _ensure_instrument(cls) -> str:
        if frappe.db.exists("Instrument", {"model": "TEST LOANER MODEL"}):
            return frappe.db.get_value("Instrument", {"model": "TEST LOANER MODEL"}, "name")
        doc = frappe.get_doc(
            {
                "doctype": "Instrument",
                "model": "TEST LOANER MODEL",
                "brand": "Test Brand",
                "serial_no": "TL-12345",
                "instrument_category": "Clarinet",
            }
        )
        doc.insert(ignore_permissions=True)
        return doc.name

    @classmethod
    def _ensure_loaner(cls, instrument: str) -> str:
        if frappe.db.exists("Loaner Instrument", {"instrument": instrument}):
            return frappe.db.get_value("Loaner Instrument", {"instrument": instrument}, "name")
        doc = frappe.get_doc(
            {
                "doctype": "Loaner Instrument",
                "instrument": instrument,
                "issue_date": nowdate(),
            }
        )
        doc.insert(ignore_permissions=True)
        return doc.name

    def test_terms_ack_required(self) -> None:
        agreement = frappe.get_doc(
            {
                "doctype": "Loaner Agreement",
                "linked_loaner": self.loaner,
                "borrower_signature": "data:image/png;base64,AAA",
                "staff_signature": "data:image/png;base64,BBB",
                "terms_ack": 0,
            }
        )
        with self.assertRaises(frappe.ValidationError):
            agreement.insert()

    def test_submit_attaches_pdf(self) -> None:
        agreement = frappe.get_doc(
            {
                "doctype": "Loaner Agreement",
                "linked_loaner": self.loaner,
                "terms_ack": 1,
                "borrower_signature": "data:image/png;base64,AAA",
                "staff_signature": "data:image/png;base64,BBB",
            }
        )
        agreement.insert()
        agreement.submit()
        agreement.reload()
        self.assertEqual(agreement.status, "Submitted")
        files = frappe.get_all(
            "File",
            filters={"attached_to_doctype": "Loaner Agreement", "attached_to_name": agreement.name},
            pluck="name",
        )
        self.assertTrue(files)
