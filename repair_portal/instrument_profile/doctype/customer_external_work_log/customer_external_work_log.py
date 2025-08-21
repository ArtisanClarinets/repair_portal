# repair_portal/instrument_profile/doctype/customer_external_work_log/customer_external_work_log.py
# Updated: 2025-06-15
# Version: 1.0
# Purpose: Controller for customer-submitted repair history logs

from frappe.model.document import Document


class CustomerExternalWorkLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		external_shop_name: DF.Data | None
		instrument: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		receipt_attachment: DF.Attach | None
		service_date: DF.Date
		service_notes: DF.Text | None
		service_type: DF.Literal["Inspection", "Setup", "Maintenance", "Repair", "Other"]
	# end: auto-generated types
	pass
