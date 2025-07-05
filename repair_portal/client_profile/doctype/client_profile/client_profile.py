# ---------------------------------------------------------------------------
# Client Profile controller – v4.1.0
# Centralizes workflow actions by calling a master handler.
# ---------------------------------------------------------------------------
from __future__ import annotations
import frappe
from frappe.model.document import Document
from repair_portal.client_profile.workflow_action_master.workflow_action_master import handle_workflow_action

class ClientProfile(Document):
    def validate(self):
        self._ensure_unique_customer()

        if self.email and frappe.db.exists(
            "Client Profile",
            {"email": self.email, "name": ["!=", self.name]}
        ):
            frappe.throw("Email already exists in another Client Profile.")

        if self.phone and frappe.db.exists(
            "Client Profile",
            {"phone": self.phone, "name": ["!=", self.name]}
        ):
            frappe.throw("Phone already exists in another Client Profile.")

    def after_insert(self):
        self._sync_contact()

    def before_workflow_action(self, action: str):
        pass

    def after_workflow_action(self, action: str):
        handle_workflow_action(self, action)

    def _ensure_unique_customer(self):
        dup = frappe.db.exists(
            "Client Profile",
            {"customer": self.customer, "name": ["!=", self.name]},
        )
        if dup:
            frappe.throw(
                f"Customer <b>{self.customer}</b> already belongs to " f"Client Profile <b>{dup}</b>."
            )

    @frappe.whitelist()
    def sync_contact(self):
        self._sync_contact()
        return True

    def _sync_contact(self):
        if not (self.email or self.phone):
            return

        contact_name = frappe.db.sql_value(
            """
            SELECT con.name FROM `tabContact` con
             JOIN `tabDynamic Link` dl
               ON dl.parent = con.name
              AND dl.link_doctype='Customer'
            WHERE dl.link_name=%s LIMIT 1
            """,
            self.customer,
        )

        contact = frappe.get_doc("Contact", contact_name) if contact_name else frappe.new_doc("Contact")

        if not contact_name:
            contact.first_name = self.client_name or self.customer
            contact.append(
                "links",
                {"link_doctype": "Customer", "link_name": self.customer},
            )

        if self.email:
            contact.set("email_ids", [])
            contact.append("email_ids", {"email_id": self.email, "is_primary": 1})

        if self.phone:
            contact.set("phone_nos", [])
            contact.append("phone_nos", {"phone": self.phone, "is_primary_mobile_no": 1})

        contact.save(ignore_permissions=True)