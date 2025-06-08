import frappe
from frappe.model.document import Document

class ClarinetInitialSetup(Document):
    def validate(self):
        if self.status == "Pass" and not self.qa_inspection:
            inspection = frappe.new_doc("Quality Inspection")
            inspection.inspection_type = "Final"
            inspection.inspection_template = "New Instrument Setup QA Template"
            inspection.reference_type = self.doctype
            inspection.reference_name = self.name
            inspection.save()
            self.qa_inspection = inspection.name
            self.db_set("qa_inspection", inspection.name)
            frappe.msgprint(f"Auto-created QA Inspection: {inspection.name}")