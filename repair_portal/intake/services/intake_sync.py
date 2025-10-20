# Path: repair_portal/intake/services/intake_sync.py
# Date: 2025-10-01
# Version: 2.0.0
# Description: Customer and contact synchronization utilities for intake workflows; creates/updates customers, contacts, and addresses with idempotent operations.
# Dependencies: frappe

from __future__ import annotations

from typing import Any

import frappe
from frappe import _


def upsert_customer(data: dict[str, Any]) -> str:
    """
    Create or update Customer, Contact, and Address from intake data.

    Args:
            data: Dictionary with keys: customer_name, email, phone, and address fields

    Returns:
            Customer name (primary key)

    Raises:
            ValidationError: If required fields are missing
    """
    # Validate required fields
    required = ["customer_name", "email", "phone"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        frappe.throw(_("Missing required customer data: {0}").format(", ".join(missing)))

    cust_name = data["customer_name"].strip()
    if not cust_name:
        frappe.throw(_("Customer name cannot be empty"))

    # Check for existing customer by name (idempotent)
    existing_cust = frappe.db.get_value("Customer", {"customer_name": cust_name}, "name")
    if existing_cust:
        customer = frappe.get_doc("Customer", existing_cust)
    else:
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": cust_name,
                "customer_type": "Individual",
                "customer_group": data.get("customer_group") or "All Customer Groups",
            }
        )
        customer.insert(ignore_permissions=True)

    # Contact (idempotent by email)
    email = data["email"].strip()
    existing_contact = frappe.db.get_value("Contact", {"email_id": email}, "name")

    if existing_contact:
        contact = frappe.get_doc("Contact", existing_contact)
        # Ensure link to customer exists
        has_link = any(
            link.link_doctype == "Customer" and link.link_name == customer.name for link in contact.links
        )
        if not has_link:
            contact.append("links", {"link_doctype": "Customer", "link_name": customer.name})
            contact.save(ignore_permissions=True)
    else:
        # Parse name for first/last
        name_parts = cust_name.split()
        first_name = name_parts[0] if name_parts else cust_name
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        contact = frappe.get_doc(
            {
                "doctype": "Contact",
                "first_name": first_name,
                "last_name": last_name,
                "email_ids": [{"email_id": email, "is_primary": 1}],
                "phone_nos": [{"phone": data["phone"], "is_primary_phone": 1}],
                "links": [{"link_doctype": "Customer", "link_name": customer.name}],
            }
        )
        contact.insert(ignore_permissions=True)

    # Address (idempotent)
    _upsert_address(customer.name, data)

    return customer.name


def _upsert_address(customer_name: str, data: dict[str, Any]) -> None:
    """
    Create or update Address for customer (idempotent).

    Args:
            customer_name: Customer primary key
            data: Dictionary with address fields (address_line1, city, state, country, pincode)
    """
    # Only create if we have address data
    if not data.get("address_line1"):
        return

    # Check for existing address linked to this customer
    addresses = frappe.get_all(
        "Dynamic Link",
        filters={"link_doctype": "Customer", "link_name": customer_name, "parenttype": "Address"},
        fields=["parent"],
    )

    if addresses:
        # Update existing
        addr = frappe.get_doc("Address", addresses[0]["parent"])
    else:
        # Create new
        addr = frappe.new_doc("Address")
        addr.append("links", {"link_doctype": "Customer", "link_name": customer_name})

    # Update fields
    addr.address_line1 = data.get("address_line1", "")
    addr.address_line2 = data.get("address_line2", "")
    addr.city = data.get("city", "")
    addr.state = data.get("state", "")
    addr.country = data.get("country", "United States")
    addr.pincode = data.get("pincode", "")

    if addr.is_new():
        addr.insert(ignore_permissions=True)
    else:
        addr.save(ignore_permissions=True)
