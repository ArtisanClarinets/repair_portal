# Path: repair_portal/api/frontend/customer_profile.py
# Date: 2025-11-30
# Version: v1.1.0
# Purpose: Customer profile view and edit endpoints for frontend use (with security hardening)
# Dependencies: frappe, api_security, error_handler, database_optimizer

import frappe
from frappe import _

from repair_portal.utils import api_security, database_optimizer, error_handler


@frappe.whitelist(allow_guest=False)
def get_customer_profile():
    """
    Returns current logged-in user's basic profile info.

    Returns:
        dict: { "full_name": ..., "email": ..., "phone": ..., "address": ... }
    """
    try:
        user = api_security.get_logged_in_user()
        profile = frappe.get_doc("User", user)
        return {
            "full_name": profile.full_name or profile.first_name or user,  # type: ignore
            "email": profile.email or profile.name,  # type: ignore
            "phone": getattr(profile, "phone", "") or "",
            "address": getattr(profile, "address", "") or "",
        }
    except Exception as e:
        error_handler.log_and_raise(e, "Failed to fetch customer profile.")  # type: ignore


@frappe.whitelist(allow_guest=False)
def update_customer_profile(full_name, email, phone=None, address=None):
    """
    Updates current user's basic profile info.

    Args:
        full_name (str): New full name
        email (str): New email
        phone (str, optional): New phone
        address (str, optional): New address

    Returns:
        dict: Confirmation
    """
    try:
        user = api_security.get_logged_in_user()
        profile = frappe.get_doc("User", user)
        
        # Validate full_name is not empty and within reasonable length
        if not full_name or not full_name.strip():
            frappe.throw(_("Full name is required"), frappe.ValidationError)
        if len(full_name) > 200:
            frappe.throw(_("Full name is too long (max 200 characters)"), frappe.ValidationError)
        
        # Validate and sanitize email
        email = (email or "").strip().lower()
        if not email:
            frappe.throw(_("Email is required"), frappe.ValidationError)
        
        # Security: Ensure the provided email address is a valid format before saving.
        # This prevents malformed data from being stored, which could impact
        # system functionality like sending notifications or password resets.
        frappe.utils.validate_email_address(email, throw=True)

        # Check email uniqueness (only if email is changing)
        current_email = (profile.email or profile.name or "").strip().lower()
        if email != current_email:
            # Check if this email is already taken by another user
            existing_user = frappe.db.get_value(
                "User",
                {"email": email, "name": ("!=", user)},
                "name"
            )
            if existing_user:
                frappe.throw(_("This email is already registered to another user"), frappe.ValidationError)
        
        # Sanitize phone (allow only digits, +, -, spaces, parentheses)
        if phone is not None:
            import re
            phone = re.sub(r"[^\d\+\-\s\(\)]", "", str(phone))[:20]
        
        # Sanitize address (limit length, strip HTML)
        if address is not None:
            from html import escape
            address = escape(str(address))[:500]
        
        # Apply updates
        profile.full_name = full_name.strip()  # type: ignore
        profile.email = email  # type: ignore
        if phone is not None:
            profile.phone = phone  # type: ignore
        if address is not None:
            profile.address = address  # type: ignore
        
        # ignore_permissions=True is acceptable here because:
        # 1. User is authenticated (allow_guest=False)
        # 2. User can only update their OWN profile (verified above)
        # 3. Only specific, validated fields are updated
        profile.save(ignore_permissions=True)
        database_optimizer.touch_user(user)  # stub, does nothing for now # type: ignore
        return {"status": "success"}
    except frappe.ValidationError:
        raise  # Re-raise validation errors as-is
    except Exception as e:
        error_handler.log_and_raise(e, "Failed to update customer profile.")  # type: ignore
