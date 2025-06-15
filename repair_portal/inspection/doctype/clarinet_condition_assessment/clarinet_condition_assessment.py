# File: repair_portal/repair_portal/inspection/doctype/clarinet_condition_assessment/clarinet_condition_assessment.py
# Updated: 2025-06-12
# Version: 1.1
# Purpose: Log assessment, load template, and trigger flows on submit

import frappe
from frappe.model.document import Document


class ClarinetConditionAssessment(Document):
    def before_insert(self):
        if self.inspection_template:
            template = frappe.get_doc('Inspection Template', self.inspection_template)
            for section in template.sections:
                sec_doc = frappe.new_doc('Inspection Checklist Section')
                sec_doc.section_title = section.section_title
                for item in section.items:
                    sec_doc.append('items', {'item_description': item.item_description})
                self.append('checklist_sections', sec_doc)

    def on_submit(self):
        if self.serial_number:
            frappe.db.set_value(
                'Instrument Tracker',
                {'serial_number': self.serial_number},
                'last_inspection',
                frappe.utils.nowdate(),
            )
        if self.instrument_condition == 'Good':
            setup = frappe.new_doc('Clarinet Initial Setup')
            setup.customer = self.customer
            setup.insert()
        else:
            repair = frappe.new_doc('Repair Log')
            repair.customer = self.customer
            repair.insert()
