from frappe import _

def get_data():
	return [
		{
			"label": _("Instrument Setup"),
			"items": [
				{"type": "doctype", "name": "Clarinet Setup Operation"}
			]
		}
	]