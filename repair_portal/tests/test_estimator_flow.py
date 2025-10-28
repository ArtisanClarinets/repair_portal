"""End-to-end tests for the clarinet estimator flow."""

from __future__ import annotations

from io import BytesIO

import frappe
from frappe.tests.utils import FrappeTestCase

from repair_portal.service_planning.clarinet_estimator import (
    UploadedPhoto,
    process_estimate_submission,
)


class TestEstimatorFlow(FrappeTestCase):
    def setUp(self) -> None:
        frappe.set_user("Administrator")
        self.customer, self.user = self._make_customer_with_user("estimator@example.com")
        self._ensure_items()
        self._ensure_pricing_rules()

    def tearDown(self) -> None:  # noqa: D401
        frappe.set_user("Administrator")

    def _make_customer_with_user(self, email: str):
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": email,
                "customer_type": "Individual",
                "email_id": email,
            }
        ).insert()
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": "Estimator",
                "send_welcome_email": 0,
                "roles": [{"role": "Customer"}],
            }
        ).insert()
        contact = frappe.get_doc(
            {
                "doctype": "Contact",
                "first_name": "Estimator",
                "last_name": "Portal",
                "user": user.name,
                "email_id": email,
            }
        ).insert()
        contact.append("links", {"link_doctype": "Customer", "link_name": customer.name})
        contact.save()
        return customer, user

    def _ensure_items(self) -> None:
        items = [
            ("PAD-BB-UPPER", 30.0),
            ("CORK-BELL", 18.0),
            ("PAD-BASS-LOWER", 38.0),
        ]
        for code, rate in items:
            if frappe.db.exists("Item", code):
                item = frappe.get_doc("Item", code)
                item.standard_rate = rate
                item.save()
                continue
            frappe.get_doc(
                {
                    "doctype": "Item",
                    "item_code": code,
                    "item_name": code,
                    "item_group": frappe.db.get_default("item_group") or "Products",
                    "stock_uom": "Nos",
                    "is_sales_item": 1,
                    "standard_rate": rate,
                }
            ).insert()

        # Additional components referenced by pricing rules
        extras = [
            ("SPRING-REGISTER", 14.0),
            ("SCREW-BRIDGE", 9.0),
            ("CORK-BARREL", 15.0),
            ("SPRING-BASS-REGISTER", 22.0),
            ("LINK-BASS-BRIDGE", 28.0),
            ("CORK-BASS-BELL", 24.0),
            ("CORK-BASS-NECK", 26.0),
        ]
        for code, rate in extras:
            if frappe.db.exists("Item", code):
                continue
            frappe.get_doc(
                {
                    "doctype": "Item",
                    "item_code": code,
                    "item_name": code,
                    "item_group": frappe.db.get_default("item_group") or "Products",
                    "stock_uom": "Nos",
                    "is_sales_item": 1,
                    "standard_rate": rate,
                }
            ).insert()

    def _ensure_pricing_rules(self) -> None:
        def upsert(data: dict) -> None:
            name = data["name"]
            if frappe.db.exists("Clarinet Estimator Pricing Rule", name):
                doc = frappe.get_doc("Clarinet Estimator Pricing Rule", name)
                for field, value in data.items():
                    if field != "doctype":
                        doc.set(field, value)
                doc.save()
            else:
                frappe.get_doc(data).insert()

        upsert(
            {
                "doctype": "Clarinet Estimator Pricing Rule",
                "name": "CEPR-BB-UPPER-TEST",
                "instrument_family": "B\u266d Clarinet",
                "region_id": "upper_stack",
                "region_label": "Upper Stack Pads",
                "component_type": "Pad",
                "task_description": "Replace and level upper stack pads",
                "part_item": "PAD-BB-UPPER",
                "part_quantity": 4,
                "labor_hours": 1.5,
                "labor_rate": 120,
                "family_multiplier": 1.0,
                "rush_multiplier": 1.25,
                "eta_days": 7,
                "priority": 5,
                "notes": "Includes seal check and tone hole polish",
            }
        )
        upsert(
            {
                "doctype": "Clarinet Estimator Pricing Rule",
                "name": "CEPR-BB-BELL-TEST",
                "instrument_family": "B\u266d Clarinet",
                "region_id": "bell_tenon",
                "region_label": "Bell Tenon",
                "component_type": "Tenon Cork",
                "task_description": "Replace bell tenon cork",
                "part_item": "CORK-BELL",
                "part_quantity": 1,
                "labor_hours": 0.5,
                "labor_rate": 115,
                "family_multiplier": 1.0,
                "rush_multiplier": 1.15,
                "eta_days": 4,
                "priority": 6,
                "notes": "Trimmed to spec with graphite burnish",
            }
        )
        upsert(
            {
                "doctype": "Clarinet Estimator Pricing Rule",
                "name": "CEPR-BASS-LOWER-TEST",
                "instrument_family": "Bass Clarinet",
                "region_id": "lower_stack",
                "region_label": "Lower Stack Pads",
                "component_type": "Pad",
                "task_description": "Bass clarinet lower stack repad",
                "part_item": "PAD-BASS-LOWER",
                "part_quantity": 6,
                "labor_hours": 2.4,
                "labor_rate": 125,
                "family_multiplier": 1.25,
                "rush_multiplier": 1.3,
                "eta_days": 9,
                "priority": 5,
                "notes": "Includes long rod refit",
            }
        )

    def test_bb_estimate_flow(self) -> None:
        frappe.set_user(self.user.name)
        result = process_estimate_submission(
            user=self.user.name,
            instrument_family="B\u266d Clarinet",
            serial="BB12345",
            condition_score=72,
            expedite=False,
            selections=["upper_stack", "bell_tenon"],
            notes="Customer reports sticky register.",
            photo_uploads=[UploadedPhoto(filename="before.jpg", content=BytesIO(b"fake-image"))],
        )
        self.assertAlmostEqual(result.total, 375.5, places=2)
        self.assertEqual(result.eta_days, 7)
        estimate = frappe.get_doc("Repair Estimate", result.estimate_name)
        self.assertEqual(estimate.customer, self.customer.name)
        self.assertEqual(len(estimate.line_items), 4)
        artifact = frappe.get_doc("Clarinet Pad Map Artifact", result.artifact_name)
        self.assertEqual(artifact.repair_estimate, estimate.name)
        self.assertEqual(len(artifact.selections), 2)
        self.assertGreaterEqual(len(artifact.photos), 1)

    def test_bass_expedite_updates_existing(self) -> None:
        frappe.set_user(self.user.name)
        first = process_estimate_submission(
            user=self.user.name,
            instrument_family="Bass Clarinet",
            serial="BASS123",
            condition_score=64,
            expedite=True,
            selections=["lower_stack"],
            notes="Rush requested for festival.",
            photo_uploads=[UploadedPhoto(filename="bass-before.jpg", content=b"img")],
        )
        self.assertAlmostEqual(first.total, 715.5, places=2)
        self.assertEqual(first.eta_days, 7)

        # Resubmit without new photos should reuse existing attachment
        follow_up = process_estimate_submission(
            user=self.user.name,
            instrument_family="Bass Clarinet",
            serial="BASS123",
            condition_score=64,
            expedite=True,
            selections=["lower_stack"],
            notes="Confirm estimate after review.",
            photo_uploads=[],
        )
        self.assertEqual(follow_up.estimate_name, first.estimate_name)
        self.assertEqual(follow_up.artifact_name, first.artifact_name)
        self.assertAlmostEqual(follow_up.total, 715.5, places=2)
        artifact = frappe.get_doc("Clarinet Pad Map Artifact", follow_up.artifact_name)
        self.assertGreaterEqual(len(artifact.photos), 1)
