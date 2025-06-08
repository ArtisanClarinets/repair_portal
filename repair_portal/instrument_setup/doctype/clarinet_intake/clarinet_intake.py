import frappe
from frappe.model.document import Document

class ClarinetIntake(Document):
    def before_save(self):
        item_group = frappe.db.get_value("Item", self.item_code, "item_group")
        if item_group != "Clarinets":
            frappe.throw("Item must belong to the 'Clarinets' Item Group.")