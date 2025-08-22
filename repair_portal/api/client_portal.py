"""
File: repair_portal/api/client_portal.py
Updated: 2025-07-13
Version: 1.4
Purpose: Secure API endpoints for client portal UI dashboard
"""

import frappe


@frappe.whitelist(allow_guest=False)
def get_my_instruments():
    """Return instrument list where the linked player belongs to the logged-in user."""
    client = frappe.db.get_value('Customer', {'linked_user': frappe.session.user}, 'name')
    if not client:
        return []

    player_names = frappe.get_all('Player Profile', {'customer': client}, pluck='name')
    return frappe.get_all(
        'Instrument Profile',
        filters={'player_profile': ['in', player_names]},
        fields=['name', 'instrument_type', 'serial_no'],
    )


@frappe.whitelist(allow_guest=False)
def get_my_repairs():
    """Return recent Repair Orders linked to instruments owned by this client."""
    client = frappe.db.get_value('Customer', {'linked_user': frappe.session.user}, 'name')
    if not client:
        return []

    player_names = frappe.get_all('Player Profile', {'customer': client}, pluck='name')
    instrument_names = frappe.get_all(
        'Instrument Profile', {'player_profile': ['in', player_names]}, pluck='name'
    )
    return frappe.get_all(
        'Repair Order',
        filters={'instrument': ['in', instrument_names]},
        fields=['name', 'status', 'instrument_name', 'modified'],
        order_by='modified desc',
        limit=10,
    )
