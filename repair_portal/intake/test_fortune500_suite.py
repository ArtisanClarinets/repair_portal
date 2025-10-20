"""Fortune-500-grade regression tests for the intake module."""

from __future__ import annotations

import contextlib
from typing import Any

import frappe
from frappe.exceptions import PermissionError, ValidationError
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from repair_portal.intake.doctype.brand_mapping_rule.brand_mapping_rule import map_brand
from repair_portal.intake.doctype.intake_session.intake_session import (
    _get_session_ttl_days,
    get_permission_query_conditions,
    has_permission,
)
from repair_portal.intake.doctype.loaner_instrument.loaner_instrument import set_loaner_status
from repair_portal.intake.doctype.loaner_agreement.loaner_agreement import (
    has_permission as loaner_agreement_has_permission,
)


class TestIntakeFortune500Suite(FrappeTestCase):
    """End-to-end coverage across intake doctypes and controllers."""

    def setUp(self) -> None:  # pragma: no cover - framework lifecycle
        super().setUp()
        frappe.set_user("Administrator")
        self.addCleanup(frappe.set_user, "Administrator")
        self.addCleanup(frappe.db.rollback)
        self._ensure_baseline_settings()
        self.test_customer = self._ensure_customer()
        self.test_price_list = self._ensure_price_list("Standard Selling")

    # ------------------------------------------------------------------
    # Fixture helpers
    # ------------------------------------------------------------------
    def _ensure_price_list(self, name: str) -> str:
        if frappe.db.exists("Price List", name):
            return name
        doc = frappe.get_doc({
            "doctype": "Price List",
            "price_list_name": name,
            "selling": 1,
        })
        doc.insert(ignore_permissions=True)
        return doc.name

    def _ensure_customer(self) -> str:
        customer_name = "QA Intake Customer"
        if frappe.db.exists("Customer", {"customer_name": customer_name}):
            return frappe.db.get_value("Customer", {"customer_name": customer_name})
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual",
            "customer_group": "All Customer Groups",
        })
        customer.insert(ignore_permissions=True)
        return customer.name

    def _ensure_item_group(self, name: str = "Instruments") -> str:
        if frappe.db.exists("Item Group", name):
            return name
        doc = frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": name,
            "parent_item_group": "All Item Groups",
            "is_group": 0,
        })
        doc.insert(ignore_permissions=True)
        return doc.name

    def _ensure_item(self, item_code: str, description: str = "QA Accessory") -> str:
        if frappe.db.exists("Item", item_code):
            return item_code
        group = self._ensure_item_group()
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": description,
            "description": description,
            "item_group": group,
            "stock_uom": "Nos",
            "is_stock_item": 0,
        })
        item.insert(ignore_permissions=True)
        return item.name

    def _ensure_baseline_settings(self) -> None:
        settings = frappe.get_doc("Clarinet Intake Settings")
        if not settings.selling_price_list:
            settings.selling_price_list = "Standard Selling"
        if not settings.stock_uom:
            settings.stock_uom = "Nos"
        settings.save(ignore_permissions=True)

    # ------------------------------------------------------------------
    # Brand Mapping Rule coverage
    # ------------------------------------------------------------------
    def test_brand_mapping_rule_normalization_and_uniqueness(self) -> None:
        rule = frappe.get_doc({
            "doctype": "Brand Mapping Rule",
            "from_brand": "  Vintage  Clarinet  Co.  ",
            "to_brand": "Vintage Clarinet Co",
        })
        rule.insert(ignore_permissions=True)
        self.addCleanup(lambda: frappe.delete_doc("Brand Mapping Rule", rule.name, ignore_permissions=True))

        reloaded = frappe.get_doc("Brand Mapping Rule", rule.name)
        self.assertEqual(reloaded.from_brand, "Vintage Clarinet Co.")
        self.assertEqual(reloaded.to_brand, "Vintage Clarinet Co")

        with self.assertRaises(ValidationError):
            dup = frappe.get_doc({
                "doctype": "Brand Mapping Rule",
                "from_brand": " vintage clarinet co. ",
                "to_brand": "Legacy Vintage",
            })
            dup.insert(ignore_permissions=True)

    def test_map_brand_cache_refresh_on_update(self) -> None:
        rule = frappe.get_doc({
            "doctype": "Brand Mapping Rule",
            "from_brand": "Modern Winds",
            "to_brand": "Modern Winds Intl",
        })
        rule.insert(ignore_permissions=True)
        self.addCleanup(lambda: frappe.delete_doc("Brand Mapping Rule", rule.name, ignore_permissions=True))

        self.assertEqual(map_brand("modern winds"), "Modern Winds Intl")

        rule.to_brand = "Modern Winds International"
        rule.save(ignore_permissions=True)

        self.assertEqual(map_brand("Modern Winds"), "Modern Winds International")

    # ------------------------------------------------------------------
    # Intake Session coverage
    # ------------------------------------------------------------------
    def test_intake_session_defaults_and_permission_guards(self) -> None:
        session = frappe.get_doc({
            "doctype": "Intake Session",
            "status": "Draft",
            "intake_json": {},
        })
        session.insert(ignore_permissions=True)
        self.addCleanup(lambda: frappe.delete_doc("Intake Session", session.name, ignore_permissions=True))

        self.assertTrue(session.session_id.startswith("ISN-"))
        self.assertEqual(session.created_by, "Administrator")
        self.assertGreaterEqual(session.expires_on, add_days(today(), 1))

        other_user = self._create_test_user("qa.intake@example.com")
        self.addCleanup(lambda: frappe.delete_doc("User", other_user, ignore_permissions=True))

        frappe.set_user(other_user)
        with self.assertRaises(PermissionError):
            session.status = "Draft"
            session.save()

        frappe.set_user("Administrator")
        self.assertEqual(get_permission_query_conditions(other_user), "(`tabIntake Session`.created_by = 'qa.intake@example.com')")
        self.assertFalse(has_permission(session, "write", other_user))
        session.status = "Submitted"
        session.save()
        self.assertTrue(has_permission(session, "read", other_user))

    def test_intake_session_ttl_configuration(self) -> None:
        original_conf = getattr(frappe.local, "conf", None)
        frappe.local.conf = frappe._dict(intake_session_ttl_days=3)
        self.addCleanup(lambda: setattr(frappe.local, "conf", original_conf))

        self.assertEqual(_get_session_ttl_days(), 3)

        frappe.local.conf = frappe._dict(intake_session_ttl_days="invalid")
        ttl = _get_session_ttl_days()
        self.assertEqual(ttl, 14)

    # ------------------------------------------------------------------
    # Intake Accessory Item coverage
    # ------------------------------------------------------------------
    def test_intake_accessory_item_autofill_and_amount(self) -> None:
        item_code = "QA-ACC-001"
        self._ensure_item(item_code)

        if not frappe.db.exists("Item Price", {"item_code": item_code, "price_list": self.test_price_list}):
            price = frappe.get_doc({
                "doctype": "Item Price",
                "price_list": self.test_price_list,
                "item_code": item_code,
                "price_list_rate": 125.50,
                "selling": 1,
            })
            price.insert(ignore_permissions=True)
            self.addCleanup(lambda: frappe.delete_doc("Item Price", price.name, ignore_permissions=True))

        accessory = frappe.new_doc("Intake Accessory Item")
        accessory.item_code = item_code
        accessory.qty = 2
        accessory.validate()

        self.assertEqual(accessory.description, "QA Accessory")
        self.assertEqual(accessory.uom, "Nos")
        self.assertEqual(accessory.rate, 125.50)
        self.assertAlmostEqual(accessory.amount, 251.0)

    # ------------------------------------------------------------------
    # Loaner Instrument coverage
    # ------------------------------------------------------------------
    def test_loaner_instrument_submit_generates_pdf_and_status(self) -> None:
        instrument = frappe.get_doc({
            "doctype": "Loaner Instrument",
            "issue_date": today(),
            "due_date": add_days(today(), 7),
            "issued_to": self.test_customer,
            "status": "Draft",
        })

        calls: dict[str, Any] = {}

        def fake_render_template(path: str, context: dict[str, Any]) -> str:
            calls["template_path"] = path
            calls["context_keys"] = sorted(context.keys())
            return "<html>Loaner Agreement</html>"

        def fake_get_pdf(html: str) -> bytes:
            calls["pdf_html"] = html
            return b"%PDF-1.4"

        class _File:
            def __init__(self, url: str) -> None:
                self.file_url = url

        def fake_save_file(filename: str, content: bytes, doctype: str, name: str, **_: Any) -> _File:
            calls["saved_file"] = filename
            self.assertEqual(doctype, "Loaner Instrument")
            self.assertEqual(name, instrument.name)
            return _File(f"/private/files/{filename}")

        with self._patched_loaner_dependencies(fake_render_template, fake_get_pdf, fake_save_file):
            instrument.insert(ignore_permissions=True)
            instrument.submit()

        self.assertEqual(instrument.status, "Issued")
        self.assertIn("template_path", calls)
        self.assertTrue(instrument.agreement_pdf)

    def test_set_loaner_status_enforces_transitions(self) -> None:
        loaner = frappe.get_doc({
            "doctype": "Loaner Instrument",
            "issue_date": today(),
            "issued_to": self.test_customer,
            "status": "Draft",
        })
        loaner.insert(ignore_permissions=True)
        self.addCleanup(lambda: frappe.delete_doc("Loaner Instrument", loaner.name, ignore_permissions=True))

        set_loaner_status(loaner.name, "Issued")
        loaner.reload()
        self.assertEqual(loaner.status, "Issued")

        set_loaner_status(loaner.name, "Returned")
        loaner.reload()
        self.assertEqual(loaner.status, "Returned")
        self.assertTrue(loaner.returned)

        with self.assertRaises(ValidationError):
            set_loaner_status(loaner.name, "Draft")

    @contextlib.contextmanager
    def _patched_loaner_dependencies(self, render_template, get_pdf, save_file):
        from repair_portal.intake.doctype.loaner_instrument import loaner_instrument as module

        original_render = module.render_template
        original_pdf = module.get_pdf
        original_save = module.save_file

        module.render_template = render_template
        module.get_pdf = get_pdf
        module.save_file = save_file
        try:
            yield
        finally:
            module.render_template = original_render
            module.get_pdf = original_pdf
            module.save_file = original_save

    # ------------------------------------------------------------------
    # Loaner Agreement coverage
    # ------------------------------------------------------------------
    def test_loaner_agreement_submission_attaches_pdf(self) -> None:
        loaner = frappe.get_doc({
            "doctype": "Loaner Instrument",
            "issue_date": today(),
            "issued_to": self.test_customer,
            "status": "Draft",
        })
        loaner.insert(ignore_permissions=True)

        agreement = frappe.get_doc({
            "doctype": "Loaner Agreement",
            "linked_loaner": loaner.name,
            "terms_ack": 1,
            "borrower_signature": "data:image/png;base64,AAA",
            "staff_signature": "data:image/png;base64,BBB",
        })

        original_get_print = frappe.get_print
        frappe.get_print = lambda *_, **__: b"Agreement"
        self.addCleanup(lambda: setattr(frappe, "get_print", original_get_print))

        agreement.insert(ignore_permissions=True)
        agreement.submit()

        files = frappe.get_all("File", filters={"attached_to_doctype": "Loaner Agreement", "attached_to_name": agreement.name})
        self.assertTrue(files)
        self.assertEqual(agreement.status, "Submitted")

    def test_loaner_agreement_permission_matrix(self) -> None:
        agreement = frappe.new_doc("Loaner Agreement")
        agreement.linked_loaner = "LOANER-TEST"
        agreement.terms_ack = 1
        agreement.borrower_signature = "sig"
        agreement.staff_signature = "sig"

        system_user = self._create_test_user("system.manager@example.com", roles=("System Manager",))
        self.addCleanup(lambda: frappe.delete_doc("User", system_user, ignore_permissions=True))
        self.assertTrue(loaner_agreement_has_permission(agreement, "write", system_user))

        reader = self._create_test_user("reader@example.com", roles=("Technician",))
        self.addCleanup(lambda: frappe.delete_doc("User", reader, ignore_permissions=True))

        original_has_permission = frappe.has_permission
        frappe.has_permission = lambda doctype, ptype=None, user=None: doctype == "Loaner Instrument"
        self.addCleanup(lambda: setattr(frappe, "has_permission", original_has_permission))

        self.assertTrue(loaner_agreement_has_permission(agreement, "read", reader))
        self.assertFalse(loaner_agreement_has_permission(agreement, "write", reader))

    # ------------------------------------------------------------------
    # Loaner Return Check coverage
    # ------------------------------------------------------------------
    def test_loaner_return_check_requires_condition_notes(self) -> None:
        check = frappe.new_doc("Loaner Return Check")
        check.damage_found = 1
        check.condition_notes = ""
        with self.assertRaises(ValidationError):
            check.validate()

        check.condition_notes = "Visible crack near the barrel."
        check.validate()  # should not raise

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _create_test_user(self, email: str, roles: tuple[str, ...] = ("Intake Coordinator",)) -> str:
        if frappe.db.exists("User", email):
            return email
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": email.split("@")[0],
            "send_welcome_email": 0,
            "roles": [{"role": role} for role in roles],
        })
        user.insert(ignore_permissions=True)
        return user.name


if __name__ == "__main__":  # pragma: no cover
    frappe.tests.run_tests(module=__file__)
