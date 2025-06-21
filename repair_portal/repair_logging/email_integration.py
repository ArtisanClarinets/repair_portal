# Path: repair_logging/email_integration.py
# Updated: 2025-06-20
# Version: 1.0
# Purpose: Inbound/outbound email routing for Customer Interaction Thread

import frappe
from frappe.utils import parse_addr


def handle_incoming_email(mail):
	from_email = parse_addr(mail.get("from"))[1]
	subject = mail.get("subject")
	content = mail.get("content")
	job_reference = None

	if "[JOB:" in subject:
		job_reference = subject.split("[JOB:")[1].split("]")[0].strip()

	if not job_reference:
		return

	thread = frappe.get_doc({
		"doctype": "Customer Interaction Thread",
		"reference_job": job_reference,
		"sender": from_email,
		"message": content,
		"via": "Email"
	})
	thread.insert(ignore_permissions=True)


def send_reply_email(to_email, subject, message, job_reference):
	frappe.sendmail(
		recipients=to_email,
		subject=f"Re: {subject} [JOB: {job_reference}]",
		message=message
	)
