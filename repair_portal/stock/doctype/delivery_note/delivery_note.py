# File: repair_portal/stock/doctype/delivery_note/delivery_note.py
# Purpose: Block delivery if linked Inspection Report has not Passed QC
# Compatible: ERPNext v15, class-based event override

import frappe
from frappe.model.document import Document


class DeliveryNote(Document):
	def validate(self):
		for item in self.items:
			if item.serial_no:
				# PATCH: Ensure serial_no exists in ERPNext Serial No
				if not frappe.db.exists("Serial No", item.serial_no):
					frappe.throw(f"Serial No '{item.serial_no}' does not exist in ERPNext!")
				status = frappe.db.get_value("Inspection Report", {"serial_no": item.serial_no}, "status")
				if status != "Passed":
					frappe.throw(
						f"Cannot deliver Serial No {item.serial_no}: QC Inspection not passed (Status: {status or 'Missing'})."
					)
