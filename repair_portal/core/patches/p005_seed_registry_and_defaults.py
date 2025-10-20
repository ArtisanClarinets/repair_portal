"""Seed roles and default settings that rely on the registry."""

from __future__ import annotations

import frappe

from repair_portal.core.registry import Role


ROLES = [role.value for role in Role]


def _ensure_role(role: str) -> None:
    if not frappe.db.exists("Role", role):
        doc = frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1})
        doc.flags.ignore_permissions = True
        doc.insert()


def execute() -> None:
    for role in ROLES:
        try:
            _ensure_role(role)
        except Exception:
            frappe.log_error("Failed to seed role", frappe.as_json({"role": role}))

    if frappe.db.table_exists("Repair Portal Settings") and not frappe.db.get_value(
        "Repair Portal Settings", None
    ):
        doc = frappe.get_doc({"doctype": "Repair Portal Settings"})
        doc.flags.ignore_permissions = True
        doc.insert()
