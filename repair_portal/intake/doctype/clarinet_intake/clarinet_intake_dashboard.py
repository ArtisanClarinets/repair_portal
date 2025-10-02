# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/doctype/clarinet_intake/clarinet_intake_dashboard.py
# Last Updated: 2025-09-19
# Version: v1.0.0
# Purpose:
#   Desk dashboard for Clarinet Intake
#   • Shows linked document counts:
#       - Instrument Inspection
#       - Clarinet Initial Setup
#       - Repair Order
#   • Displays an activity heatmap (Created → Submitted → Delivered) via timeline data provider
#
# Notes:
#   - Counts use `fieldname` / `non_standard_fieldnames` mapping below.
#   - Heatmap pulls data from clarinet_intake_timeline.get_timeline_data if present.

from __future__ import annotations

from frappe import _


def get_data():
	"""
	Returns the dashboard configuration dictionary for Clarinet Intake.
	Frappe automatically renders:
	  • Linked document counts from `transactions`
	  • A heatmap if `heatmap` is True (using `get_timeline_data` if provided)
	"""
	return {
		# Default link field name used by *most* linked doctypes to refer back to Clarinet Intake
		# (We use 'intake' because Clarinet Initial Setup & Repair Order link with this field.)
		"fieldname": "intake",

		# When linked doctypes use a different field, declare it here for accurate counts.
		"non_standard_fieldnames": {
			"Instrument Inspection": "intake_record_id",  # inspection stores the intake's name in intake_record_id
			"Clarinet Initial Setup": "intake",
			"Repair Order": "intake",
		},

		# Group linked doctypes into labeled sections
		"transactions": [
			{
				"label": _("Quality"),
				"items": ["Instrument Inspection", "Clarinet Initial Setup"],
			},
			{
				"label": _("Service"),
				"items": ["Repair Order"],
			},
		],

		# Enable activity heatmap on the form
		"heatmap": True,
		"heatmap_message": _(
			"Activity density (created, submitted, delivered). Hover dots for details."
		),

		# If your app provides a custom timeline data source, wire it here.
		# This path should resolve to a function with signature:
		#   get_timeline_data(doctype: str, name: str) -> Dict[str, int]
		# It should return a mapping of 'YYYY-MM-DD' -> count.
		"get_timeline_data": "repair_portal.intake.doctype.clarinet_intake.clarinet_intake_timeline.get_timeline_data",

		# Optional quick links to internal fields on this doctype (left empty by default).
		# Example to expose the Instrument link on the form header:
		# "internal_links": {
		# 	"instrument": ["Instrument", "instrument"]
		# }
	}
