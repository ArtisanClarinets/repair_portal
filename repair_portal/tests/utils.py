"""Utility functions reused by tests and operational runbooks."""

from __future__ import annotations

import frappe


def portal_login_smoke(role: str = "Customer") -> str:
    """Return the first user assigned to the given role, raising if missing."""

    user = frappe.db.get_value("Has Role", {"role": role}, "parent")
    if not user:
        raise frappe.DoesNotExistError(f"No user with role {role}")
    print(f"First user with role {role}: {user}")
    return user


def assert_customer_portal_guards(role: str = "Customer") -> None:
    """Ensure the selected role cannot read internal QA records."""

    user = portal_login_smoke(role)
    has_access = frappe.permissions.has_permission(
        "Final QA Checklist", ptype="read", user=user
    )
    if has_access:
        raise PermissionError("Customer role should not access Final QA Checklist")
    print("Portal guard check passed for Final QA Checklist")
