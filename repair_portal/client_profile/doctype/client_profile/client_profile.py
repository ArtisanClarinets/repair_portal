import frappe
from frappe.model.document import Document

class ClientProfile(Document):
    def autoname(self):
        last = frappe.db.sql(
            "select max(cast(substr(client_profile_id, 4) as unsigned)) from `tabClient Profile`"
        )
        next_number = (last[0][0] or 0) + 1
        self.client_profile_id = "CP-" + str(next_number).zfill(6)

    def validate(self):
        self.ensure_unique_user()

    def ensure_unique_user(self):
        if self.linked_user:
            exists = frappe.db.exists("Client Profile", {
                "linked_user": self.linked_user,
                "name": ["!=", self.name]
            })
            if exists:
                frappe.throw(
                    f"This User is already linked to another Client Profile: {exists}"
                )

    def validate_activation_requirements(self):
        missing = []
        if not self.client_name:
            missing.append("Client Name")
        if not self.customer:
            missing.append("Customer (Link to Customer record)")
        if not self.email:
            missing.append("Email Address")
        # Add other required fields if needed

        if missing:
            frappe.throw(
                "Cannot activate client profile. The following required fields are missing: <br><ul>{}</ul>".format(
                    "".join([f"<li>{f}</li>" for f in missing])
                )
            )

    def on_update(self):
        if self.has_value_changed("profile_status"):
            if self.profile_status == "Active":
                # Block activation if requirements are not met
                self.validate_activation_requirements()
                # Ensure at least one player profile exists
                players = frappe.get_all("Player Profile", filters={"client_profile": self.name})
                if not players:
                    player_profile = frappe.get_doc({
                        "doctype": "Player Profile",
                        "client_profile": self.name,
                        "player_name": self.client_name
                    })
                    player_profile.insert(ignore_permissions=True)
                    self.add_comment("Workflow", "Auto-created a Player Profile on activation.")
                if self.linked_user and self.email:
                    frappe.sendmail(
                        recipients=[self.email],
                        subject="Your Artisan Clarinets account is now active",
                        message="Welcome! Your account is now active."
                    )
                self.add_comment("Workflow", "Client profile activated.")
            elif self.profile_status == "Archived":
                # Archive all Player Profiles and linked Instruments
                players = frappe.get_all("Player Profile", filters={"client_profile": self.name})
                for pp in players:
                    pp_doc = frappe.get_doc("Player Profile", pp)
                    pp_doc.profile_status = "Archived"
                    pp_doc.save(ignore_permissions=True)
                    instruments = frappe.get_all("Instrument Profile", filters={"player_profile": pp_doc.name})
                    for ip in instruments:
                        ip_doc = frappe.get_doc("Instrument Profile", ip)
                        ip_doc.status = "Inactive"
                        ip_doc.save(ignore_permissions=True)
                self.add_comment("Workflow", "Client profile and all linked profiles archived.")
