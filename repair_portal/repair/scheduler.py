# File: repair_portal/repair/scheduler.py
# Created: 2025-06-15
# Purpose: Daily SLA checker that flags breached repair orders and sends alerts

import frappe
from frappe.utils import today


def check_sla_breaches():
	overdue = frappe.get_all(
		"Repair Order",
		filters={
			"status": ["not in", ["Closed"]],
			"promised_date": ["<", today()],
			"sla_breached": 0,
		},
		fields=["name", "promised_date"],
	)

	for ro in overdue:
		doc = frappe.get_doc("Repair Order", ro.name)
		doc.sla_breached = 1
		doc.save()
		frappe.sendmail(
			recipients=["service@artisanclarinets.com"],
			subject=f"[ALERT] SLA Breached: {ro.name}",
			message=f"Repair Order {ro.name} has breached its SLA. Promised date: {ro.promised_date}",
		)
