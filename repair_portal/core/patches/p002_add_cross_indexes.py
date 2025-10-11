"""Add cross-module indexes for performance."""

from __future__ import annotations

import frappe

INDEXES = {
    "Repair Order": [
        ("workflow_state", "idx_repair_order_workflow"),
        ("status", "idx_repair_order_status"),
        ("technician", "idx_repair_order_technician"),
        ("customer", "idx_repair_order_customer"),
        ("instrument_serial", "idx_repair_order_serial"),
    ],
    "Repair Material Movement": [
        ("repair_order", "idx_rmm_order"),
        ("item_code", "idx_rmm_item"),
    ],
    "Repair Labor Session": [
        ("repair_order", "idx_rls_order"),
        ("technician", "idx_rls_technician"),
    ],
}


def execute() -> None:
    for doctype, index_list in INDEXES.items():
        for column, name in index_list:
            if not frappe.db.has_index(doctype, name):
                frappe.db.add_index(doctype, column, index_name=name)
