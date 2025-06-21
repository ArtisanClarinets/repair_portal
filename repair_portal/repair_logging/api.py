# Path: repair_logging/api.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: API endpoints for Customer Interaction Thread (SMS + frontend integrations)

import frappe
from frappe import _
from frappe.utils import now
from werkzeug.wrappers import Response
from twilio.rest import Client

@frappe.whitelist(allow_guest=True)
def receive_sms():
	from_number = frappe.form_dict.get("From")
	to_number = frappe.form_dict.get("To")
	message_body = frappe.form_dict.get("Body")

	# Simplified mapping logic
	job = frappe.db.get_value("Job", {"customer_phone": ["like", f"%{from_number[-6:]}%"]}, "name")
	if not job:
		return Response("No matching job", status=404)

	doc = frappe.get_doc({
		"doctype": "Customer Interaction Thread",
		"reference_job": job,
		"sender": from_number,
		"message": message_body,
		"via": "SMS"
	})
	doc.insert(ignore_permissions=True)
	return Response("OK", status=200)

@frappe.whitelist()
def send_sms_from_thread(phone, message):
	settings = frappe.get_single("Repair Portal Settings")
	client = Client(settings.twilio_sid, settings.twilio_token)
	client.messages.create(
		to=phone,
		from_=settings.twilio_number,
		body=message
	)
	return True