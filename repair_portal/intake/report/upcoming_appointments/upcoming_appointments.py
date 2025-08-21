# Report: Upcoming Appointments
# Module: Intake
# Updated: 2025-06-12

import frappe


def execute(filters=None):
	columns = [
		{
			"fieldname": "appointment_date",
			"label": "Appointment Date",
			"fieldtype": "Datetime",
			"width": 180,
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 180,
		},
		{
			"fieldname": "serial_no",
			"label": "Instrument Serial",
			"fieldtype": "Data",
			"width": 140,
		},
		{"fieldname": "reason", "label": "Reason", "fieldtype": "Small Text", "width": 200},
		{"fieldname": "confirmed", "label": "Confirmed", "fieldtype": "Check", "width": 100},
	]

	data = frappe.get_all(
		"Appointment",
		fields=["appointment_date", "customer", "serial_no", "reason", "confirmed"],
		filters={"appointment_date": [">=", frappe.utils.now()]}, # type: ignore
		order_by="appointment_date asc",
	)

	return columns, data
