# relative path: intake/doctype/loaner_instrument/loaner_instrument.py
# updated: 2025-07-17
# version: 1.1
# purpose: Adds auto-PDF generation and digital agreement signing for loaner issuance. Now includes Fortune-500 error handling for generate_loaner_agreement.

import frappe
from frappe.model.document import Document
from frappe.utils.file_manager import save_file
from frappe.utils.jinja import render_template
from frappe.utils.pdf import get_pdf


class LoanerInstrument(Document):
	def after_insert(self):
		if self.issued_to and not self.returned:
			self.generate_loaner_agreement()

	def generate_loaner_agreement(self):
		"""
		Generate, attach, and notify for the loaner agreement PDF.

		Args:
		    self: LoanerInstrument Doc instance

		Returns:
		    None. Attaches PDF and notifies user.

		On failure, logs error for audit.
		"""
		try:
			# Prepare context for Jinja2 template
			context = {"doc": self, "customer": frappe.get_doc("Customer", self.issued_to)}
			html = render_template("repair_portal/intake/templates/loaner_agreement_template.html", context)
			pdf = get_pdf(html)
			filename = f"LoanerAgreement_{self.name}.pdf"
			save_file(filename, pdf, self.doctype, self.name, is_private=1)
			frappe.msgprint("Loaner agreement PDF generated and attached.")
		except Exception:
			frappe.log_error(frappe.get_traceback(), "LoanerInstrument: generate_loaner_agreement failed")
			frappe.msgprint("There was an error generating the loaner agreement PDF. Please contact support.")
