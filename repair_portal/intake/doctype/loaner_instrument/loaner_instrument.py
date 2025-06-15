# relative path: intake/doctype/loaner_instrument/loaner_instrument.py
# updated: 2025-06-15
# version: 1.0
# purpose: Adds auto-PDF generation and digital agreement signing for loaner issuance

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
        context = {'doc': self, 'customer': frappe.get_doc('Customer', self.issued_to)}
        html = render_template(
            'repair_portal/intake/templates/loaner_agreement_template.html', context
        )
        pdf = get_pdf(html)
        filename = f'LoanerAgreement_{self.name}.pdf'
        save_file(filename, pdf, self.doctype, self.name, is_private=1)
        frappe.msgprint('Loaner agreement PDF generated and attached.')
