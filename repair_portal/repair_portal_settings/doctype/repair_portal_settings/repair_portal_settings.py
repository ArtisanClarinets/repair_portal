"""Repair Portal Settings DocType controller."""

from __future__ import annotations

from frappe.model.document import Document


class RepairPortalSettings(Document):
    """Singleton settings backing repair portal configuration."""

    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        hours_per_day: DF.Data | None
        intake_session_ttl_days: DF.Int
        standard_hourly_rate: DF.Currency
    # end: auto-generated types

    pass
