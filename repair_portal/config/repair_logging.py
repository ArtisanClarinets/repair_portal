from frappe import _

def get_data():
	return [
		{
			"label": _("Repair Logging"),
			"items": [
				{"type": "doctype", "name": "Tool Usage Log"}
			]
		}
	]