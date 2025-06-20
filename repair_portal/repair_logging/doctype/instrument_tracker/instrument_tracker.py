"""
repair_logging/doctype/instrument_tracker/instrument_tracker.py
Instrument Tracker
Version 1.0
Last Updated: 2025-06-09

Handles tracking of instrument interaction logs and propagates related interaction references to linked Customer and Item documents.
"""

import frappe
from frappe.model.document import Document


class InstrumentTracker(Document):
    def on_update(self):
        self.update_related_links()

    def update_related_links(self):
        if not self.customer or not self.item_code:
            return

        customer_doc = frappe.get_doc('Customer', self.customer)
        item_doc = frappe.get_doc('Item', self.item_code)

        customer_doc.set('related_interactions', [])
        item_doc.set('related_interactions', [])

        for log in self.interaction_logs:
            base = {
                'instrument_tracker': self.name,
                'interaction_type': log.interaction_type,
                'reference_doctype': log.reference_doctype,
                'reference_name': log.reference_name,
                'date': log.date,
                'notes': log.notes,
            }
            customer_doc.append('related_interactions', base)
            item_doc.append('related_interactions', base)

        customer_doc.save(ignore_permissions=True)
        item_doc.save(ignore_permissions=True)
