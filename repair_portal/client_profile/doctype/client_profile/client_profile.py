# ---------------------------------------------------------------------------
# Client Profile controller – v4.0.0
# Centralizes workflow actions by calling a master handler.
# ---------------------------------------------------------------------------
from __future__ import annotations
import frappe
from frappe.model.document import Document
# --- NEW: Import the master workflow handler ---
from repair_portal.client_profile.workflow_action_master.workflow_action_master import handle_workflow_action

class ClientProfile(Document):
    # ---------------------------------------------------------------------
    # Hooks
    # ---------------------------------------------------------------------
    def validate(self):
        """
        Runs before the document is saved.
        """
        self._ensure_unique_customer()

    def after_insert(self):
        """
        Runs after the document is first saved to the database.
        """
        self._sync_contact()

    def before_workflow_action(self, action: str):
        """
        Hook before any workflow transition.
        (No changes needed here)
        """
        pass

    def after_workflow_action(self, action: str):
        """
        Hook after any workflow transition.
        --- REPLACED: This now calls the centralized master handler. ---
        """
        handle_workflow_action(self, action)

    # ---------------------------------------------------------------------
    # Validation Helpers (Kept in controller)
    # ---------------------------------------------------------------------
    def _ensure_unique_customer(self):
        """
        Prevents creating a duplicate Client Profile for the same Customer.
        """
        dup = frappe.db.exists(
            "Client Profile",
            {"customer": self.customer, "name": ["!=", self.name]},
        )
        if dup:
            frappe.throw(
                f"Customer <b>{self.customer}</b> already belongs to " f"Client Profile <b>{dup}</b>."
            )

    # --- REMOVED: All workflow-specific methods have been moved ---
    # The following methods are no longer needed in this file:
    # - _validate_activation_requirements()
    # - _handle_activation()
    # - _archive_children()

    # ---------------------------------------------------------------------
    # Contact Sync (Kept in controller for UI interaction)
    # ---------------------------------------------------------------------
    @frappe.whitelist()
    def sync_contact(self):
        """
        Exposed to the client-side scripts; allows a user to manually
        re-run the sync after editing the email or phone number.
        """
        self._sync_contact()
        return True

    def _sync_contact(self):
        """
        Finds or creates a Contact document for the linked Customer
        and keeps the primary email/phone in sync.
        """
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


# --- REMOVED: Global helper function is no longer needed here ---
# The _set_state() function has been moved to workflow_action_master.py