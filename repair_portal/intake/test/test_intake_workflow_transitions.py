# File: test_intake_workflow_transitions.py
# Purpose: Validates intake workflow state transitions and allowed actions
# Last Updated: 2025-07-17
# Version: 0.1

import frappe
import pytest


def create_intake_doc(owner):
    # Helper to create a minimal intake doc
    return frappe.get_doc(
        {
            'doctype': 'Clarinet Intake',
            'owner': owner,
            'intake_type': 'Inventory',
            'serial_no': 'TEST-SERIAL-001',
        }
    ).insert(ignore_permissions=True)


def test_workflow_transitions():
    # Use System Manager for full permission
    frappe.set_user('Administrator')
    doc = create_intake_doc(owner='test1@example.com')

    # Initial state
    assert doc.workflow_state == 'Draft'

    # Simulate submit
    doc.submit()
    doc.reload()
    assert doc.workflow_state in ['Submitted', 'In Progress', 'Open']  # Adjust per your workflow

    # Simulate archive/cancel
    doc.cancel()
    doc.reload()
    assert doc.workflow_state in ['Cancelled', 'Archived']  # Adjust per your workflow

    # Permission assertions (optional)
    frappe.set_user('customer1@example.com')
    assert doc.has_permission('read')
    # ...add more permission checks as needed
