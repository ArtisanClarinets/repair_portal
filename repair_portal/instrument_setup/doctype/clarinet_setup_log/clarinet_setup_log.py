# File: repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_log/clarinet_setup_log.py
# Updated: 2025-06-12
# Version: 1.1
# Purpose: Controller for Clarinet Setup Log; supports documentation and auditing setup actions

from frappe.model.document import Document


class ClarinetSetupLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		action_by: DF.Link | None
		attachments: DF.Attach | None
		customer: DF.Link
		description: DF.Text | None
		initial_setup: DF.Link
		instrument_profile: DF.Link
		log_time: DF.Datetime | None
		notes: DF.Text | None
		serial: DF.Link
	# end: auto-generated types
	pass
