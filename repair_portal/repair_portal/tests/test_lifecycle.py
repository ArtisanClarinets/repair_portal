"""Lifecycle tests for key repair_portal modules."""
from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate

from repair_portal.repair_portal.api.portal import prepare_quote_and_deposit
from repair_portal.repair_portal.inventory import material_planner
from repair_portal.repair_portal.report import deposit_collection_summary
from repair_portal.repair_portal.service_plans import automation as service_plan_automation


class DummyPaymentRequest:
    """Lightweight stand-in for ERPNext Payment Request during tests."""

    def __init__(self, data: dict[str, object]):
        self.__dict__.update(data)
        self.name = data.get("name") or f"PR-{frappe.generate_hash(length=6)}"
        self.flags = frappe._dict(ignore_permissions=False)
        self.status = data.get("status", "Draft")
        self.grand_total = data.get("grand_total", 0)

    def insert(self, ignore_permissions: bool = False) -> "DummyPaymentRequest":
        return self

    def submit(self) -> None:
        self.status = "Submitted"

    def save(self, ignore_permissions: bool = False) -> None:  # pragma: no cover - interface completeness
        return None

    def get_payment_url(self) -> str:
        return f"https://payments.example/{self.name}"


class DummyStockEntry:
    """Simple substitute for Stock Entry during unit tests."""

    def __init__(self) -> None:
        self.items: list[frappe._dict] = []
        self.flags = frappe._dict(ignore_permissions=False)
        self.name = None
        self.purpose = None
        self.company = None

    def append(self, fieldname: str, values: dict[str, object]) -> None:
        if fieldname == "items":
            self.items.append(frappe._dict(values))

    def get(self, fieldname: str, default=None):  # pragma: no cover - doc compat
        if fieldname == "items":
            return self.items
        return getattr(self, fieldname, default)

    def insert(self, ignore_permissions: bool = False) -> "DummyStockEntry":
        if not self.name:
            self.name = f"STE-{frappe.generate_hash(length=5)}"
        return self

    def submit(self) -> None:
        if not self.name:
            self.name = f"STE-{frappe.generate_hash(length=5)}"


class RepairPortalLifecycleTest(FrappeTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.company = cls._ensure_company()
        cls.customer = cls._ensure_customer()
        cls.item = cls._ensure_item()
        cls.instrument = cls._ensure_instrument()
        cls.service_plan = cls._ensure_service_plan()
        cls.stock_item = cls._ensure_stock_item()
        cls.warehouse = cls._ensure_warehouse()

    @classmethod
    def _ensure_company(cls) -> str:
        company = frappe.db.get_value("Company", {}, "name")
        if company:
            return company
        doc = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": "Portal Clarinet Co",
                "abbr": "PCC",
                "default_currency": "USD",
                "country": "United States",
            }
        )
        doc.insert()
        return doc.name

    @classmethod
    def _ensure_customer(cls) -> str:
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Test Clarinet Studio " + frappe.generate_hash(length=4),
                "customer_group": "All Customer Groups",
                "territory": "All Territories",
            }
        )
        customer.insert()
        return customer.name

    @classmethod
    def _ensure_item(cls) -> str:
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": "REPAIR-PLAN-" + frappe.generate_hash(length=5),
                "item_name": "Repair Plan Item",
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
                "is_stock_item": 0,
            }
        )
        item.insert()
        return item.name

    @classmethod
    def _ensure_stock_item(cls) -> str:
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": "STOCK-" + frappe.generate_hash(length=5),
                "item_name": "Stock Pad",
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
                "is_stock_item": 1,
            }
        )
        item.insert()
        return item.name

    @classmethod
    def _ensure_warehouse(cls) -> str:
        warehouse = frappe.get_doc(
            {
                "doctype": "Warehouse",
                "warehouse_name": "Main Bench " + frappe.generate_hash(length=4),
                "company": cls.company,
            }
        )
        warehouse.insert()
        return warehouse.name

    @classmethod
    def _ensure_instrument(cls) -> str:
        instrument = frappe.get_doc(
            {
                "doctype": "Instrument",
                "customer": cls.customer,
                "serial_no": "SERIAL-" + frappe.generate_hash(length=8),
                "make": "Yamaha",
                "model": "Custom",
                "family": "Bb",
                "finish": "Silver",
            }
        )
        instrument.insert()
        return instrument.name

    @classmethod
    def _ensure_service_plan(cls) -> str:
        plan = frappe.get_doc(
            {
                "doctype": "Service Plan",
                "item": cls.item,
                "coverage_months": 12,
                "included_services": "Quarterly adjustment",
                "pricing_tier": "Plus",
                "auto_renew": 1,
            }
        )
        plan.insert()
        return plan.name

    def test_rental_activation_and_return(self) -> None:
        original_table_exists = frappe.db.table_exists

        def fake_table_exists(name: str) -> bool:
            if name in {"tabSubscription", "tabSubscription Plan", "tabDelivery Note", "tabSales Invoice"}:
                return False
            return original_table_exists(name)

        rental = frappe.get_doc(
            {
                "doctype": "Rental Contract",
                "customer": self.customer,
                "company": self.company,
                "instrument": self.item,
                "serial_no": "RC-" + frappe.generate_hash(length=6),
                "start_date": nowdate(),
                "due_date": nowdate(),
                "billing_plan": "Monthly",
            }
        )
        with patch("frappe.db.table_exists", side_effect=fake_table_exists):
            rental.insert()
            rental.status = "Active"
            rental.save()
            rental.reload()
            self.assertEqual(rental.workflow_state, "Active")
            self.assertTrue(rental.barcode)
            rental.status = "Returned"
            rental.save()
            rental.reload()
            self.assertEqual(rental.workflow_state, "Returned")
            self.assertIsNotNone(rental.return_date)

    def test_service_plan_activation_sets_portal_token(self) -> None:
        enrollment = frappe.get_doc(
            {
                "doctype": "Service Plan Enrollment",
                "customer": self.customer,
                "company": self.company,
                "instrument": self.instrument,
                "service_plan": self.service_plan,
                "start_date": nowdate(),
                "billing_frequency": "Monthly",
            }
        )
        with patch("frappe.db.table_exists", side_effect=lambda name: False if name in {"tabSubscription", "tabSubscription Plan"} else frappe.db.has_table(name)):
            enrollment.insert()
            enrollment.status = "Active"
            enrollment.save()
            enrollment.reload()
            self.assertEqual(enrollment.workflow_state, "Active")
            self.assertTrue(enrollment.portal_token)

    def test_warranty_claim_syncs_repair_flag(self) -> None:
        claim = frappe.new_doc("Warranty Claim")
        claim.repair_order = "REPAIR-TEST"
        claim.claim_status = "Approved"
        with patch("frappe.db.exists", return_value=True), patch("frappe.db.set_value") as setter:
            claim._sync_repair_flag()
            setter.assert_any_call("Repair Order", "REPAIR-TEST", "warranty_flag", 1)

    def test_deposit_collection_report_returns_hours(self) -> None:
        estimate = frappe.get_doc(
            {
                "doctype": "Repair Estimate",
                "customer": self.customer,
                "instrument": self.instrument,
                "deposit_amount": 150,
            }
        )
        estimate.sent_on = datetime.utcnow() - timedelta(hours=6)
        estimate.approved_on = datetime.utcnow()
        estimate.insert()
        columns, rows = deposit_collection_summary.execute()
        self.assertTrue(any(row.get("hours_to_approve") is not None for row in rows))

    def test_prepare_quote_and_deposit_creates_payment_request(self) -> None:
        template = frappe.get_doc(
            {
                "doctype": "Repair Class Template",
                "default_labor_hours": 2,
                "upsell_options": [
                    {
                        "doctype": "Class Upsell",
                        "item": self.item,
                        "price": 75,
                        "description": "Premium barrel refit",
                    }
                ],
            }
        )
        template.insert()

        repair_order = frappe.get_doc(
            {
                "doctype": "Repair Order",
                "customer": self.customer,
                "instrument": self.instrument,
                "planned_hours": 3,
                "repair_class": template.name,
                "priority": "Normal",
            }
        )
        repair_order.insert()

        original_get_value = frappe.db.get_value

        def fake_get_value(*args, **kwargs):
            if args and args[0] == "Payment Gateway Account":
                return "Test-Stripe"
            return original_get_value(*args, **kwargs)

        original_get_doc = frappe.get_doc

        def fake_get_doc(*args, **kwargs):
            if args and isinstance(args[0], dict) and args[0].get("doctype") == "Payment Request":
                return DummyPaymentRequest(args[0])
            return original_get_doc(*args, **kwargs)

        previous_ratio = getattr(frappe.conf, "repair_portal_deposit_ratio", None)
        frappe.conf.repair_portal_deposit_ratio = 0.5

        with patch("frappe.db.get_value", side_effect=fake_get_value), patch(
            "frappe.get_doc", side_effect=fake_get_doc
        ):
            result = prepare_quote_and_deposit(
                repair_order.name,
                repair_class=template.name,
                upsells=[self.item],
            )

        if previous_ratio is None:
            delattr(frappe.conf, "repair_portal_deposit_ratio")
        else:
            frappe.conf.repair_portal_deposit_ratio = previous_ratio

        self.assertGreater(result["deposit_amount"], 0)
        self.assertTrue(result["payment_request"])
        self.assertTrue(result["payment_url"]) 

    def test_reserve_and_issue_materials(self) -> None:
        repair_order = frappe.get_doc(
            {
                "doctype": "Repair Order",
                "customer": self.customer,
                "instrument": self.instrument,
                "planned_hours": 1,
                "priority": "Normal",
            }
        )
        repair_order.insert()
        row = repair_order.append(
            "planned_materials",
            {
                "item": self.stock_item,
                "qty": 2,
                "warehouse": self.warehouse,
            },
        )
        repair_order.save()

        with patch(
            "repair_portal.repair_portal.inventory.material_planner._create_material_request",
            return_value="MR-PLAN-1",
        ), patch("frappe.msgprint"):
            response = material_planner.reserve_stock(repair_order.name)

        self.assertEqual(response["status"], "reserved")
        self.assertEqual(response["material_request"], "MR-PLAN-1")
        self.assertEqual(
            frappe.db.get_value("Planned Material", row.name, "reservation_entry"),
            "MR-PLAN-1",
        )

        original_new_doc = frappe.new_doc

        def fake_new_doc(doctype: str, *args, **kwargs):
            if doctype == "Stock Entry":
                return DummyStockEntry()
            return original_new_doc(doctype, *args, **kwargs)

        with patch("frappe.new_doc", side_effect=fake_new_doc), patch("frappe.msgprint"):
            issue_response = material_planner.issue_to_job(repair_order.name)

        self.assertEqual(issue_response["status"], "issued")
        actual_rows = frappe.get_all(
            "Actual Material", filters={"parent": repair_order.name}, fields=["name"]
        )
        self.assertTrue(actual_rows)

    def test_service_plan_autopay_creates_payment_request(self) -> None:
        enrollment = frappe.get_doc(
            {
                "doctype": "Service Plan Enrollment",
                "customer": self.customer,
                "company": self.company,
                "instrument": self.instrument,
                "service_plan": self.service_plan,
                "start_date": nowdate(),
                "billing_frequency": "Monthly",
                "status": "Active",
                "auto_pay_enabled": 1,
                "next_billing_date": nowdate(),
            }
        )
        enrollment.insert()

        previous_gateway = getattr(frappe.conf, "repair_portal_stripe_gateway", None)
        frappe.conf.repair_portal_stripe_gateway = "Stripe-Gateway"

        original_get_doc = frappe.get_doc

        def fake_get_doc(*args, **kwargs):
            if args and isinstance(args[0], dict) and args[0].get("doctype") == "Payment Request":
                return DummyPaymentRequest(args[0])
            return original_get_doc(*args, **kwargs)

        with patch(
            "repair_portal.repair_portal.service_plans.automation.determine_plan_rate",
            return_value=45,
        ), patch("frappe.get_doc", side_effect=fake_get_doc):
            service_plan_automation.create_payment_request(enrollment)

        enrollment.reload()

        if previous_gateway is None:
            delattr(frappe.conf, "repair_portal_stripe_gateway")
        else:
            frappe.conf.repair_portal_stripe_gateway = previous_gateway

        self.assertIsNotNone(enrollment.last_billed_on)
        self.assertIsNotNone(enrollment.next_billing_date)

