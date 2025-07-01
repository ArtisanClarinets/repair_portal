# repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.py
# Updated: 2025-07-01
# Version: 1.3.0
# Purpose: Instrument Profile controller with field change tracking

import frappe
from frappe import _
from frappe.model.document import Document


class InstrumentProfile(Document):
    def validate(self):
        self.ensure_unique_serial()
        self.update_history_on_change()

    def ensure_unique_serial(self):
        if self.serial:
            exists = frappe.db.exists(
                "Instrument Profile", {"serial": self.serial, "name": ("!=", self.name)}
            )
            if exists:
                frappe.throw(_(f"An Instrument Profile already exists for Serial #: {self.serial}"))

    def update_history_on_change(self):
        if not self.get("document_history"):
            return
        event_types = ["Serial Changed", "Owner Changed", "Status Changed"]
        changes = []

        for event in event_types:
            if self.has_value_changed(event):
                changes.append(event)
                self.append(
                    "document_history",
                    {
                        "event_date": frappe.utils.now_datetime(),
                        "event_type": event,
                        "reference_doc": self.name,
                        "summary": f"{event} detected.",
                        "user": frappe.session.user,
                    },
                )

        if changes:
            frappe.msgprint(_(f"Document History updated: {', '.join(changes)}"))

    def has_value_changed(self, event):
        before = self.get_doc_before_save()
        if not before:
            return False

        if event == "Serial Changed":
            return before.serial != self.serial
        if event == "Owner Changed":
            return before.owner != self.owner
        if event == "Status Changed":
            return before.status != self.status

        return False

    def on_trash(self):
        self.archive_profile()

    def archive_profile(self):
        frappe.db.set_value(self.doctype, self.name, "is_archived", 1)

    def generate_qr_link(self):
        base_url = frappe.utils.get_url()
        public_link = f"{base_url}/instrument-profile/{self.name}"
        return public_link
