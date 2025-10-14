"""Install-time seeding for core Email Group dependencies."""

from __future__ import annotations

import frappe


def ensure_email_groups() -> None:
    """Create required Email Group records before Singles defaults are applied."""
    frappe.db.commit()

    required_groups: tuple[tuple[str, str], ...] = (
        ("Player Newsletter", "Player Newsletter"),
    )

    has_email_group_name = frappe.db.has_column("Email Group", "email_group_name")

    for title, group_name in required_groups:
        existing = frappe.db.exists("Email Group", group_name)
        if not existing:
            existing = frappe.db.exists("Email Group", {"title": title})

        if existing:
            continue

        doc = frappe.get_doc({
            "doctype": "Email Group",
            "title": title,
        })

        if has_email_group_name:
            doc.email_group_name = group_name  # type: ignore[attr-defined]
        else:
            doc.name = group_name  # fallback for legacy schemas

        try:
            doc.insert(ignore_permissions=True)
        except frappe.DuplicateEntryError:
            continue
        except Exception:
            frappe.db.rollback()
            raise

    frappe.db.commit()
