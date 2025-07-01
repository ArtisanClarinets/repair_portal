# ---------------------------------------------------------------------------
# Client Profile controller – v3.0.0
# Compatible with Client Profile Workflow
# ---------------------------------------------------------------------------
from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import get_url


class ClientProfile(Document):
    # ---------------------------------------------------------------------
    # Hooks
    # ---------------------------------------------------------------------
    def validate(self):
        self._ensure_unique_customer()

        if self.profile_status == "Active":
            self._validate_activation_requirements()

    def after_insert(self):
        self._sync_contact()

    def before_workflow_action(self, action):
        """Hook before any workflow transition."""
        # Add logic if needed per action
        pass

    def after_workflow_action(self, action):
        """Hook after any workflow transition."""
        if self.profile_status == "Active":
            self._handle_activation()

        elif self.profile_status == "Archived":
            self._archive_children()

    # ---------------------------------------------------------------------
    # Validation helpers
    # ---------------------------------------------------------------------
    def _ensure_unique_customer(self):
        dup = frappe.db.exists(
            "Client Profile",
            {"customer": self.customer, "name": ["!=", self.name]},
        )
        if dup:
            frappe.throw(
                f"Customer <b>{self.customer}</b> already belongs to " f"Client Profile <b>{dup}</b>."
            )

    def _validate_activation_requirements(self):
        cust = frappe.get_doc("Customer", self.customer)
        missing = [
            label
            for field, label in [("customer_name", "Customer Name"), ("email_id", "Email")]
            if not cust.get(field)
        ]
        if missing:
            frappe.throw(
                "Cannot activate; fix Customer master:<br><ul>"
                + "".join(f"<li>{m}</li>" for m in missing)
                + "</ul>"
            )

    # ---------------------------------------------------------------------
    # Workflow handlers
    # ---------------------------------------------------------------------
    def _handle_activation(self):
        self._validate_activation_requirements()

        if not frappe.db.exists("Player Profile", {"client_profile": self.name}):
            frappe.get_doc(
                {
                    "doctype": "Player Profile",
                    "client_profile": self.name,
                    "player_name": frappe.db.get_value("Customer", self.customer, "customer_name"),
                }
            ).insert(ignore_permissions=True)
            self.add_comment("Workflow", "Auto-created first Player Profile.")

        email = frappe.db.get_value("Customer", self.customer, "email_id")
        if email:
            try:
                frappe.enqueue(
                    "frappe.core.doctype.communication.email.sendmail",
                    queue="short",
                    recipients=[email],
                    subject="Your Artisan Clarinets portal is live",
                    message=(
                        "Welcome! Manage your repairs online at "
                        f"<a href='{get_url('/login')}'>{get_url('/login')}</a>"
                    ),
                )
            except Exception:
                frappe.log_error(frappe.get_traceback(), "ClientProfile: welcome-email failure")

    def _archive_children(self):
        players = frappe.get_all("Player Profile", {"client_profile": self.name})
        for p in players:
            pp = frappe.get_doc("Player Profile", p.name)
            _set_state(pp, "Archived")

            instruments = frappe.get_all("Instrument Profile", {"player_profile": pp.name})
            for i in instruments:
                ip = frappe.get_doc("Instrument Profile", i.name)
                _set_state(ip, "Archived")

        self.add_comment("Workflow", "All child Player and Instrument Profiles archived.")

    # ---------------------------------------------------------------------
    # Contact sync
    # ---------------------------------------------------------------------
    @frappe.whitelist()
    def sync_contact(self):
        """Expose to JS; re-run after the user edits phone/e-mail."""
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


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _set_state(doc: Document, state: str):
    """Helper to set a workflow state field consistently."""
    if hasattr(doc, "profile_status"):
        doc.profile_status = state
    elif hasattr(doc, "workflow_state"):
        doc.workflow_state = state
    doc.save(ignore_permissions=True)
