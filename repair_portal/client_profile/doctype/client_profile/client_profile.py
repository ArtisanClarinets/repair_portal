# Relative Path: repair_portal/client_profile/doctype/client_profile/client_profile.py
# Last Updated: 2025-07-13
# Version: v4.2
# Purpose: Validates, syncs, and automates Client Profile behavior (Customer creation, rename propagation, audit trail)
# Dependencies: Customer, Contact, Sales Order, Repair Ticket, Consent Log

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

        if self.is_new() is False and not self.change_reason:
            frappe.throw("Please specify a reason for the update (change_reason).")

    def after_insert(self):
        self._sync_contact()
        self._create_customer_if_missing()

    def on_rename(self, old_name, new_name, merge=False):
        try:
            for doctype in ["Sales Order", "Repair Ticket"]:
                frappe.db.sql(
                    f"""
                    UPDATE `tab{doctype}`
                       SET client_profile = %s
                     WHERE client_profile = %s
                    """,
                    (new_name, old_name),
                )
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "ClientProfile.on_rename failed")

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
                f"Customer <b>{self.customer}</b> already belongs to "
                f"Client Profile <b>{dup}</b>."
            )

    def _create_customer_if_missing(self):
        if not frappe.db.exists("Customer", self.customer):
            try:
                frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": self.client_name,
                    "customer_type": "Individual",
                    "customer_group": "All Customer Groups",
                    "territory": "All Territories"
                }).insert(ignore_permissions=True)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "ClientProfile: Customer creation failed")

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
            contact.append("links", {"link_doctype": "Customer", "link_name": self.customer})

        if self.email:
            contact.set("email_ids", [])
            contact.append("email_ids", {"email_id": self.email, "is_primary": 1})

        if self.phone:
            contact.set("phone_nos", [])
            contact.append("phone_nos", {"phone": self.phone, "is_primary_mobile_no": 1})

        contact.save(ignore_permissions=True)