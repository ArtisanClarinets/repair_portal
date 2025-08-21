# repair_portal/instrument_profile/cron/warranty_expiry_check.py
# Updated: 2025-06-15
# Version: 1.0
# Purpose: Daily check for warranties expiring in the next 30 days

import frappe
from frappe.utils import add_days, nowdate


def execute():
	today = nowdate()
	threshold = add_days(today, 30)

	instruments = frappe.get_all(
		"Instrument Profile",
		filters={"warranty_end_date": ["between", [today, threshold]]},
		fields=["name", "owner_name", "serial_no", "warranty_end_date"],
	)

	for inst in instruments:
		frappe.sendmail(
			recipients=["admin@artisanclarinets.com"],
			subject=f"Warranty Expiry Notice: {inst.serial_no} ({inst.owner_name})",
			message=f"Instrument {inst.name} will expire on {inst.warranty_end_date}. Consider reaching out to the customer.",
		)
