# Path: qa/config/desktop.py
# Version: v1.0
# Updated: 2025-06-11
# Purpose: Define the QA module for the Frappe Desk UI

from frappe import _


def get_data():
	return [
		{
			"module_name": "QA",
			"type": "module",
			"label": _("Quality Assurance"),
			"icon": "octicon octicon-check",
			"color": "red",
			"description": "Final quality control and checklists",
		}
	]
