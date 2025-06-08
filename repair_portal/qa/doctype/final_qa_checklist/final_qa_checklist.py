import frappe
from frappe.model.document import Document

class FinalQAChecklist(Document):

    def validate(self):
        if not self.inspector:
            frappe.throw("Inspector is required.")

        if not self.pass_all_tests:
            frappe.msgprint("Please confirm that all QA tests have been passed.")