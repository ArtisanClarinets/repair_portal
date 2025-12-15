# Copyright (c) 2025, Dylan Thompson and Contributors
# See license.txt

import frappe
import pytest

from frappe.tests.utils import FrappeTestCase


class TestRepairOrder(FrappeTestCase):
    def make_customer(self):
        return frappe.get_doc({"doctype": "Customer", "customer_name": "Test Customer"}).insert()

    def make_warehouse(self):
        # Try to reuse an existing warehouse when available for speed
        wh = frappe.db.get_value("Warehouse", None)
        if wh:
            return frappe.get_doc("Warehouse", wh)
        company = frappe.db.get_default("company") or "Test Company"
        return frappe.get_doc({"doctype": "Warehouse", "warehouse_name": "Test WH", "company": company}).insert()

    def ensure_labor_item(self):
        if frappe.db.exists("Item", "LABOR-SERVICE"):
            return frappe.get_doc("Item", "LABOR-SERVICE")
        return frappe.get_doc({"doctype": "Item", "item_code": "LABOR-SERVICE", "item_name": "Labor Service", "item_group": frappe.db.get_default("item_group") or "Services", "stock_uom": "Nos", "is_sales_item": 0}).insert()

    def test_workflow_default_and_transitions(self):
        customer = self.make_customer()
        warehouse = self.make_warehouse()
        labor = self.ensure_labor_item()

        ro = frappe.get_doc({
            "doctype": "Repair Order",
            "customer": customer.name,
            "warehouse_source": warehouse.name,
            "labor_item": labor.name,
        }).insert()

        # Default state should be the first entry in WORKFLOW_SEQUENCE (Requested)
        self.assertEqual(ro.workflow_state, "Requested")

        # Legal progression: Requested -> Quoted -> In Progress -> Ready for QA -> Completed -> Delivered
        ro.workflow_state = "Quoted"
        ro.save()
        ro.reload()
        self.assertEqual(ro.workflow_state, "Quoted")

        ro.workflow_state = "In Progress"
        ro.save()
        ro.reload()
        self.assertEqual(ro.workflow_state, "In Progress")

        ro.workflow_state = "Ready for QA"
        ro.save()
        ro.reload()
        self.assertEqual(ro.workflow_state, "Ready for QA")

        ro.workflow_state = "Completed"
        ro.save()
        ro.reload()
        self.assertEqual(ro.workflow_state, "Completed")

        ro.workflow_state = "Delivered"
        ro.save()
        ro.reload()
        self.assertEqual(ro.workflow_state, "Delivered")

    def test_illegal_transition_raises(self):
        customer = self.make_customer()
        warehouse = self.make_warehouse()
        labor = self.ensure_labor_item()

        ro = frappe.get_doc({
            "doctype": "Repair Order",
            "customer": customer.name,
            "warehouse_source": warehouse.name,
            "labor_item": labor.name,
        }).insert()

        # Illegal: Requested -> Completed (should raise ValidationError)
        ro.workflow_state = "Completed"
        with pytest.raises(frappe.ValidationError):
            ro.save()
