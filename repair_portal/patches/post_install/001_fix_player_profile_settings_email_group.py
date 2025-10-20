"""Post-install fix for Player Profile Settings newsletter email group link."""

from __future__ import annotations

import frappe

from repair_portal.install.seed_email_groups import ensure_email_groups


DOCTYPE = "Player Profile Settings"
FIELDNAME = "newsletter_email_group"
REQUIRED_GROUP = "Player Newsletter"


def execute() -> None:
    """Ensure metadata and data for the Player Profile Settings email group are valid."""
    frappe.reload_doc("player_profile", "doctype", "player_profile_settings")

    frappe.db.sql(
        """
        UPDATE `tabDocField`
           SET options = %s
         WHERE parent = %s
           AND fieldname = %s
           AND (options IS NULL OR options != %s)
        """,
        ("Email Group", DOCTYPE, FIELDNAME, "Email Group"),
    )

    ensure_email_groups()

    settings = frappe.get_single(DOCTYPE)
    current_value = getattr(settings, FIELDNAME, None)
    if current_value and not frappe.db.exists("Email Group", current_value):
        setattr(settings, FIELDNAME, None)
        settings.save(ignore_permissions=True)

    if not frappe.db.exists("Email Group", REQUIRED_GROUP):
        doc = frappe.get_doc(
            {
                "doctype": "Email Group",
                "title": REQUIRED_GROUP,
            }
        )
        if frappe.db.has_column("Email Group", "email_group_name"):
            doc.email_group_name = REQUIRED_GROUP  # type: ignore[attr-defined]
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
