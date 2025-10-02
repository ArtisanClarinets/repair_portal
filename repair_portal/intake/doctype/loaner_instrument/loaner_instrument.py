# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/doctype/loaner_instrument/loaner_instrument.py
# Last Updated: 2025-09-19
# Version: v2.1.0 (on_submit PDF, idempotent attach, guarded transitions)
# Purpose:
#   Minimal workflow for issuing/returning a loaner instrument with signed agreement PDF.
#   • Status: Draft → Issued → Returned
#   • on_submit(): generate and attach agreement PDF (idempotent)
#   • Guards: cannot Return before Issued; due_date ≥ issue_date; returned flag syncs with status
# Dependencies:
#   - frappe (v15)
#   - HTML template at: repair_portal/intake/templates/loaner_agreement_template.html

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
from frappe.utils.file_manager import save_file
from frappe.utils.jinja import render_template
from frappe.utils.pdf import get_pdf

TEMPLATE_PATH = "repair_portal/intake/templates/loaner_agreement_template.html"


class LoanerInstrument(Document):
	# ---------------------------------------------------------------------
	# Validation & lifecycle
	# ---------------------------------------------------------------------
	def validate(self) -> None:
		self._normalize_status_flags()
		self._validate_dates()
		self._validate_business_rules()

	def on_submit(self) -> None:
		"""
		When the loaner is submitted, mark as Issued (if Draft) and generate agreement PDF.
		Idempotent: if agreement already attached, do nothing.
		"""
		if self.status in (None, "", "Draft"):
			self.db_set("status", "Issued", update_modified=False)

		self._generate_agreement_pdf_if_needed()

	# ---------------------------------------------------------------------
	# Business rules & helpers
	# ---------------------------------------------------------------------
	def _normalize_status_flags(self) -> None:
		# Keep 'returned' flag in sync with status
		if self.status == "Returned":
			self.returned = 1  # type: ignore
		elif self.status in ("Draft", "Issued"):
			self.returned = 0  # type: ignore

	def _validate_dates(self) -> None:
		if not self.issue_date:
			frappe.throw(_("Issue Date is required."))
		if self.due_date and getdate(self.due_date) < getdate(self.issue_date):
			frappe.throw(_("Due Date cannot be before Issue Date."))

	def _validate_business_rules(self) -> None:
		# Issued requires a recipient
		if self.status in ("Issued", "Returned") and not (self.issued_to or self.issued_contact):
			frappe.throw(_("Please set 'Issued To (Customer or Contact)' before issuing or returning."))

		# Cannot return before issued
		if self.status == "Returned" and self.flags.in_insert == False:
			# If moving to Returned, ensure we were Issued at some point (docstatus 1 or status Issued)
			previous = frappe.db.get_value(self.doctype, self.name, ["docstatus", "status"], as_dict=True) if self.name else None
			if previous and previous.get("docstatus") == 0 and previous.get("status") not in ("Issued",):
				frappe.throw(_("Cannot mark Returned before the loaner is Issued."))

		# If Returned, prompt for condition_on_return (optional but recommended)
		if self.status == "Returned" and not self.condition_on_return:
			frappe.msgprint(
				_("Consider recording 'Condition on Return' for audit."), indicator="yellow"
			)

	def _generate_agreement_pdf_if_needed(self) -> None:
		"""
		Render Jinja template to PDF and attach once. Set agreement_pdf (Attach field) to file URL.
		"""
		try:
			# Skip if already attached and file exists
			if self.agreement_pdf and frappe.db.exists("File", {"file_url": self.agreement_pdf}):
				return

			context = self._build_template_context()
			html = render_template(TEMPLATE_PATH, context)
			pdf_bytes = get_pdf(html)

			filename = f"LoanerAgreement_{self.name}.pdf"
			file_doc = save_file(
				filename,
				pdf_bytes,
				self.doctype,
				self.name,
				is_private=1,
				decode=False,
			)
			# Persist file URL into the Attach field
			self.db_set("agreement_pdf", file_doc.file_url, update_modified=False)
			frappe.msgprint(_("Loaner agreement PDF generated and attached."))

		except Exception:
			frappe.log_error(
				title="LoanerInstrument.on_submit (PDF generation)",
				message=frappe.get_traceback(),
			)
			frappe.msgprint(
				_("There was an error generating the loaner agreement PDF. Please contact support."),
				indicator="red",
			)

	def _build_template_context(self) -> dict:
		"""Collect related docs and pre-computed values for the template."""
		customer = None
		if self.issued_to and frappe.db.exists("Customer", self.issued_to):
			customer = frappe.get_doc("Customer", self.issued_to)

		contact = None
		if self.issued_contact and frappe.db.exists("Contact", self.issued_contact):
			contact = frappe.get_doc("Contact", self.issued_contact)

		instrument = None
		if self.instrument and frappe.db.exists("Instrument", self.instrument):
			instrument = frappe.get_doc("Instrument", self.instrument)

		intake = None
		if self.intake and frappe.db.exists("Clarinet Intake", self.intake):
			intake = frappe.get_doc("Clarinet Intake", self.intake)

		def _sig_url(val: str | None) -> str | None:
			if not val:
				return None
			# If already a data URL, keep as-is; else convert to absolute URL
			if isinstance(val, str) and val.startswith("data:"):
				return val
			return frappe.utils.get_url(val)

		return {
			"doc": self,
			"customer": customer,
			"contact": contact,
			"instrument": instrument,
			"intake": intake,
			"customer_signature_url": _sig_url(getattr(self, "customer_signature", None)),
			"company_rep_signature_url": _sig_url(getattr(self, "company_rep_signature", None)),
			"company": frappe.defaults.get_global_default("company"),
			"company_full_name": frappe.db.get_value("Company", frappe.defaults.get_global_default("company"), "company_name"),
		}


# -------------------------------------------------------------------------
# Optional: Controlled status transition API (can be called from buttons)
# -------------------------------------------------------------------------
@frappe.whitelist()
def set_loaner_status(name: str, new_status: str) -> None:
	"""
	Safely update the loaner status with business-rule enforcement.
	Allowed transitions:
	  Draft -> Issued
	  Issued -> Returned
	"""
	if new_status not in ("Draft", "Issued", "Returned"):
		frappe.throw(_("Invalid status."))

	doc: LoanerInstrument = frappe.get_doc("Loaner Instrument", name)  # type: ignore

	# Permission guard
	if not doc.has_permission("write"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	current = doc.status or "Draft"

	if current == "Draft" and new_status == "Issued":
		doc.status = "Issued"
	elif current == "Issued" and new_status == "Returned":
		doc.status = "Returned"
		doc.returned = 1  # type: ignore
	else:
		frappe.throw(_("Illegal transition from {0} to {1}.").format(current, new_status))

	doc.save()
