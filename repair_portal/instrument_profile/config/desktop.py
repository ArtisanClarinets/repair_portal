# File: repair_portal/instrument_profile/config/desktop.py
# Created: 2025-06-13
# Version: 1.0
# Purpose: Defines Instrument Profile module card for Desk


def get_data():
	return [
		{
			"module_name": "Instrument Profile",
			"label": "Instrument Profile",
			"color": "blue",
			"icon": "octicon octicon-device-camera",
			"type": "module",
			"description": "Instrument profiles for clients and inventory.",
		}
	]
