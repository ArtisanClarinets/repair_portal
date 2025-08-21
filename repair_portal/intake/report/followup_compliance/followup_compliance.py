# File Header Template
# Relative Path: repair_portal/intake/report/followup_compliance/followup_compliance.py
# Last Updated: 2025-07-05
# Version: v2.0
# Purpose: Runtime-filtered report showing the compliance rate of Intake Follow-ups.
#          Accepts status and date-range filters; rows are ordered by follow-up date DESC.
# Dependencies: frappe, repair_portal.logger
#
# Usage example:
#   filters = {
#       "status": "Completed",
#       "from_date": "2025-01-01",
#       "to_date": "2025-06-30"
#   }
#   columns, data = execute(filters)

from __future__ import annotations

import frappe
from frappe import _

from repair_portal.logger import get_logger

LOGGER = get_logger("report.followup_compliance")


# --------------------------------------------------------------------------- #
#  Public API (Frappe Report entry-point)
# --------------------------------------------------------------------------- #
def execute(filters: dict | None = None) -> tuple[list[dict], list[dict]]:
	"""Return report columns & rows based on runtime *filters*.

	Args:
	    filters: Optional dict with keys:
	        • status (str) – filter by follow-up *Status*.
	        • from_date (date|str) – include records on/after this date.
	        • to_date   (date|str) – include records on/before this date.

	Returns:
	    (columns, data): Tuple where *columns* is a list of column definitions
	    and *data* is a list of row dicts suitable for Frappe’s report engine.
	"""
	filters = filters or {}

	# Build dynamic SQL conditions & params
	conditions: list[str] = []
	params: dict = {}

	status = filters.get("status")
	if status:
		conditions.append("f.status = %(status)s")
		params["status"] = status

	from_date = filters.get("from_date")
	if from_date:
		conditions.append("f.followup_date >= %(from_date)s")
		params["from_date"] = from_date

	to_date = filters.get("to_date")
	if to_date:
		conditions.append("f.followup_date <= %(to_date)s")
		params["to_date"] = to_date

	condition_sql = " AND ".join(conditions)
	if condition_sql:
		condition_sql = "WHERE " + condition_sql

	query = f"""
        SELECT
            f.customer              AS customer,
            f.status                AS status,
            f.followup_date         AS followup_date,
            i.workflow_state        AS intake_state
        FROM `tabIntake Followup` AS f
        LEFT JOIN `tabClarinet Intake` AS i
          ON i.name = f.parent
        {condition_sql}
        ORDER BY f.followup_date DESC
    """

	LOGGER.debug("Running Follow-up Compliance query: %s", query)
	data = frappe.db.sql(query, params, as_dict=True)

	columns = _get_columns()
	return columns, data


# --------------------------------------------------------------------------- #
#  Internal helpers
# --------------------------------------------------------------------------- #
def _get_columns() -> list[dict]:
	"""Define report columns (labels translated)."""
	return [
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 200,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Follow-up Date"),
			"fieldname": "followup_date",
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"label": _("Intake State"),
			"fieldname": "intake_state",
			"fieldtype": "Data",
			"width": 120,
		},
	]
