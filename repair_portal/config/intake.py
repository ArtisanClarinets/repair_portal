from frappe import _

def get_data():
	return [
		{
			"label": _("Intake"),
			"items": [
				{"type": "doctype", "name": "Customer Consent Form"}
			]
		}
	]