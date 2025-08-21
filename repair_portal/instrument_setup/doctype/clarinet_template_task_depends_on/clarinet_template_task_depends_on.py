# Path: repair_portal/repair_portal/instrument_setup/doctype/clarinet_template_task_depends_on/clarinet_template_task_depends_on.py
# Date: 2025-08-16
# Version: 1.0.0
# Description: Server controller for Clarinet Template Task Depends On child table; handles template-level task dependencies.
# Dependencies: frappe, frappe.model.document

from frappe.model.document import Document


class ClarinetTemplateTaskDependsOn(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		sequence: DF.Int
	# end: auto-generated types
	"""Child table storing template-level task dependencies for setup templates."""
	pass
