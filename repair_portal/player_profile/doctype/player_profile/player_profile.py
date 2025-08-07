# File Header Template
# Relative Path: repair_portal/player_profile/doctype/player_profile/player_profile.py
# Last Updated: 2025-07-20
# Version: v2.0
# Purpose: Core business logic and automation for Player Profile (CRM), covering full musician lifecycle, preferences, marketing, compliance, and CRM triggers.
# Dependencies: Customer, Instrument Profile, Sales Invoice, Repair Log, Email Group Member, Frappe/ERPNext APIs

from datetime import datetime

import frappe
from frappe.model.document import Document


class PlayerProfile(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from repair_portal.customer.doctype.instruments_owned.instruments_owned import InstrumentsOwned
        from repair_portal.player_profile.doctype.player_equipment_preference.player_equipment_preference import PlayerEquipmentPreference

        affiliation: DF.Data | None
        communication_preference: DF.Literal["Email", "SMS", "Phone Call"]
        customer_lifetime_value: DF.Currency
        equipment_preferences: DF.Table[PlayerEquipmentPreference]
        g_sharp_a_connection: DF.Data | None
        instruments_owned: DF.Table[InstrumentsOwned]
        intonation_notes: DF.SmallText | None
        key_height_preference: DF.Literal["Low/Close", "Standard", "High/Open"]
        last_visit_date: DF.Date | None
        mailing_address: DF.SmallText | None
        newsletter_subscription: DF.Check
        player_level: DF.Literal["Student (Beginner)", "Student (Advanced)", "Amateur/Hobbyist", "University Student", "Professional (Orchestral)", "Professional (Jazz/Commercial)", "Educator", "Collector"]
        player_name: DF.Data
        player_profile_id: DF.Data
        preferred_name: DF.Data | None
        preferred_pad_type: DF.Data | None
        primary_email: DF.Data
        primary_phone: DF.Data | None
        primary_playing_styles: DF.Check
        primary_teacher: DF.Data | None
        profile_creation_date: DF.Date | None
        profile_status: DF.Literal["Draft", "Active", "Archived"]
        referral_source: DF.Data | None
        spring_tension_preference: DF.Literal["Light/Fluid", "Standard/Firm", "Heavy/Resistant"]
        targeted_marketing_optin: DF.Check
        technician_notes: DF.SmallText | None
    # end: auto-generated types
    """
    Player Profile - Persistent CRM profile for a unique musician/player.
    Handles full identity, musical, equipment, service preferences, analytics, permissions, and CRM automations.
    Args:
        Document: Frappe/ERPNext base document
    Returns:
        None
    """
    def autoname(self):
        if not self.player_profile_id or self.player_profile_id == "New":
            self.player_profile_id = f"PLAYER-{frappe.generate_hash(length=5).upper()}"

    def validate(self):
        """
        Ensures required fields, compliance logic, and triggers downstream CRM actions.
        """
        # Core field checks
        if not self.player_name:
            frappe.throw("Full Name is required for Player Profile.")
        if not self.primary_email:
            frappe.throw("Primary Email is required for Player Profile.")
        # COPPA/child privacy (if date of birth is present)
        if hasattr(self, "date_of_birth") and self.date_of_birth:
            try:
                age = (datetime.now().date() - self.date_of_birth).days // 365
                if age < 13:
                    self._block_marketing_emails()
            except Exception:
                frappe.log_error(frappe.get_traceback(), "PlayerProfile.validate failed on DOB")

        # CRM triggers (opt-ins)
        if self.newsletter_subscription:
            self._sync_email_group()

        # Auto-set creation date if not set
        if not self.profile_creation_date:
            self.profile_creation_date = frappe.utils.today()

        # Sync owned instruments list (links)
        self._sync_instruments_owned()
        self._calc_lifetime_value()

    def _block_marketing_emails(self):
        """
        Unsubscribes user if under 13, notifies parent/guardian.
        """
        try:
            if self.primary_email:
                frappe.db.set_value("Email Group Member", {"email": self.primary_email}, "unsubscribed", 1)
            # Notify parent/client user if available
            customer = frappe.db.get_value("Customer", {"email_id": self.primary_email}, ["linked_user"], as_dict=True)
            if customer and customer.linked_user:
                parent_email = frappe.db.get_value("User", customer.linked_user, "email")
                if parent_email:
                    subject = f"Profile Marketing Blocked for {self.player_name}"
                    message = f"Dear Parent/Guardian,<br>Due to compliance, marketing emails for {self.player_name} have been blocked (age under 13). No action is required.<br>Thank you!<br>— The Artisan Clarinets Team"
                    frappe.sendmail(recipients=[parent_email], subject=subject, message=message)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: block_marketing_emails notification failed")

    def _sync_email_group(self):
        """
        Syncs the player to newsletter or marketing groups if opted-in.
        """
        try:
            if self.primary_email:
                frappe.get_doc({
                    "doctype": "Email Group Member",
                    "email": self.primary_email,
                    "email_group": "Player Newsletter"
                }).insert(ignore_permissions=True, ignore_if_duplicate=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: sync_email_group failed")

    def _sync_instruments_owned(self):
        """
        Updates the instruments_owned child table from linked Instrument Profile docs.
        """
        try:
            owned = frappe.get_all(
                "Instrument Profile",
                filters={"owner_player": self.name},
                fields=["name", "serial_no", "model"]
            )
            self.set("instruments_owned", [])
            for row in owned:
                self.append("instruments_owned", {
                    "name": row["name"],
                    "serial_no": row.get("serial_no"),
                    "model": row.get("model")
                })
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: sync_instruments_owned failed")

    def _calc_lifetime_value(self):
        """
        Calculates Customer Lifetime Value based on linked Sales Invoices.
        """
        try:
            invoices = frappe.get_all(
                "Sales Invoice",
                filters={"player_profile": self.name, "docstatus": 1},
                fields=["grand_total"]
            )
            self.customer_lifetime_value = sum(inv["grand_total"] for inv in invoices) if invoices else 0
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: calc_lifetime_value failed")

    def on_update(self):
        """
        Called on every save; handles CRM triggers (like/notify), analytics, and logging.
        """
        try:
            # CRM Notification Example: If a "liked" instrument is available, trigger notification
            for liked in self.get("instruments_liked") or []:
                instrument = frappe.get_doc("Instrument Profile", liked.instrument)
                if instrument.status == "Available":
                    self._notify_liked_instrument(instrument)
            # Staff Notes handling (running log)
            # No duplicate notes; always log new note if present
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: on_update CRM triggers failed")

    def _notify_liked_instrument(self, instrument):
        """
        Notifies the player when a liked instrument becomes available.
        """
        try:
            if self.primary_email:
                subject = f"Your Liked Instrument {instrument.name} is Now Available!"
                message = f"Hi {self.preferred_name or self.player_name},<br><br>Your liked instrument <b>{instrument.name}</b> is now in stock! <a href='/app/instrument-profile/{instrument.name}'>View Details</a>.<br><br>— The Artisan Clarinets Team"
                frappe.sendmail(recipients=[self.primary_email], subject=subject, message=message)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: notify_liked_instrument failed")
