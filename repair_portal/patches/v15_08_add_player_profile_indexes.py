"""Add indexes and Sales Invoice custom field for Player Profile integrations."""

from __future__ import annotations

from typing import Iterable, Sequence

import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

LOGGER = frappe.logger("player_profile_migration")

PLAYER_PROFILE_INDEXES: Sequence[tuple[str, Sequence[str]]] = (
    ("Player Profile", ("player_name",)),
    ("Player Profile", ("primary_email",)),
    ("Player Profile", ("player_level",)),
    ("Player Profile", ("profile_status",)),
    ("Sales Invoice", ("player_profile",)),
)


def execute() -> None:
    """Ensure Sales Invoice is indexed and Player Profile queries stay performant."""

    _ensure_sales_invoice_custom_field()
    for doctype, columns in PLAYER_PROFILE_INDEXES:
        _add_index(doctype, columns)


def _ensure_sales_invoice_custom_field() -> None:
    if frappe.db.has_column("Sales Invoice", "player_profile"):
        return

    LOGGER.info("Creating Sales Invoice player_profile custom field")
    create_custom_fields(
        {
            "Sales Invoice": [
                {
                    "fieldname": "player_profile",
                    "label": "Player Profile",
                    "fieldtype": "Link",
                    "options": "Player Profile",
                    "insert_after": "customer",
                    "in_standard_filter": 1,
                    "description": _("Linked Player Profile for CLV tracking"),
                }
            ]
        },
        update=True,
    )


def _add_index(doctype: str, columns: Iterable[str]) -> None:
    table = f"tab{doctype}"
    index_name = "idx_" + "_".join([doctype.lower().replace(" ", "_")] + [col for col in columns])

    try:
        if frappe.db.has_index(table, index_name):
            return
    except Exception:
        # has_index may not exist on all database adapters
        pass

    LOGGER.info("Ensuring index", extra={"doctype": doctype, "columns": list(columns)})
    try:
        frappe.db.add_index(doctype, list(columns), index_name=index_name)
    except AttributeError:
        # Fallback to SQL if add_index is unavailable (rare)
        cols = ", ".join(f"`{col}`" for col in columns)
        frappe.db.sql(f"CREATE INDEX `{index_name}` ON `{table}` ({cols})")
    except Exception:
        frappe.log_error(
            title="PlayerProfile Index Creation",
            message=frappe.get_traceback(),
        )
*** End of File
