import frappe
from frappe.model.document import Document

class RepairInspection(Document):
	def before_save(self):
		self.set_defaults()

	def set_defaults(self):
		# Example defaulting logic – extend as needed
		if not self.inspection_date:
			self.inspection_date = frappe.utils.nowdate()

		if not self.status:
			self.status = "Pending"

		# Add additional logic and modularize if this grows large

	def validate(self):
		# Add any validation checks
		if not self.instrument_serial:
			frappe.throw("Instrument serial is required.")