# Copyright (c) 2025, DT and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RepairPortalSettings(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        hours_per_day: DF.Data | None
        standard_hourly_rate: DF.Currency
    # end: auto-generated types
    pass
