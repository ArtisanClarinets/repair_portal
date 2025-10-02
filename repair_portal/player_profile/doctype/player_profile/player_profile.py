# Path: repair_portal/player_profile/doctype/player_profile/player_profile.py
# Date: 2025-10-02
# Version: 3.0.0
# Description: Fortune-500 production Player Profile controller with CRM, preferences, marketing compliance,
#              comprehensive validation, security hardening, and complete lifecycle management.
# Dependencies: Customer, Instrument Profile, Sales Invoice, Email Group Member, Frappe/ERPNext v15 APIs

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now, today

if TYPE_CHECKING:
    from frappe.types import DF

    from repair_portal.customer.doctype.instruments_owned.instruments_owned import (
        InstrumentsOwned,
    )
    from repair_portal.player_profile.doctype.player_equipment_preference.player_equipment_preference import (
        PlayerEquipmentPreference,
    )


def _resolve_serial_display(instrument_profile_row: dict) -> str | None:
    """
    Returns a human-friendly serial string to display in 'instruments_owned'.
    
    Handles multiple serial number storage formats:
    - Direct serial_no field (string)
    - Link to Instrument Serial Number (ISN) DocType
    - ERPNext Serial No
    
    Args:
        instrument_profile_row: Dict containing instrument profile data
        
    Returns:
        Human-readable serial number string or None
    """
    if instrument_profile_row.get("serial_no"):
        return instrument_profile_row.get("serial_no")

    instrument_name = instrument_profile_row.get("instrument")
    if not instrument_name:
        return None

    try:
        # Get Instrument.serial_no value and its field type
        serial_value = frappe.db.get_value("Instrument", instrument_name, "serial_no")
        if not serial_value:
            return None

        # Determine fieldtype dynamically
        df = frappe.get_meta("Instrument").get_field("serial_no")
        fieldtype = getattr(df, "fieldtype", None) if df else None

        if fieldtype == "Link" and frappe.db.exists("Instrument Serial Number", serial_value):
            return frappe.db.get_value("Instrument Serial Number", serial_value, "serial")

        # Legacy Data or ERPNext Serial No docname stored as Data
        return serial_value
    except Exception:
        frappe.log_error(
            frappe.get_traceback(), f"PlayerProfile: Failed to resolve serial for {instrument_name}"
        )
        return None


class PlayerProfile(Document):
    """
    Player Profile - Production CRM profile for musicians/players.
    
    Manages comprehensive player data including:
    - Identity and contact information
    - Musical background and preferences
    - Equipment and technical preferences
    - Service history and notes
    - Marketing preferences and compliance
    - Lifetime value tracking
    """

    # begin: auto-generated types
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
    player_level: DF.Literal[
        "Student (Beginner)",
        "Student (Advanced)",
        "Amateur/Hobbyist",
        "University Student",
        "Professional (Orchestral)",
        "Professional (Jazz/Commercial)",
        "Educator",
        "Collector",
    ]
    player_name: DF.Data
    player_profile_id: DF.Data
    preferred_name: DF.Data | None
    preferred_pad_type: DF.Data | None
    primary_email: DF.Data
    primary_phone: DF.Data | None
    primary_playing_styles: DF.SmallText | None
    primary_teacher: DF.Data | None
    profile_creation_date: DF.Date | None
    profile_status: DF.Literal["Draft", "Active", "Archived"]
    referral_source: DF.Data | None
    spring_tension_preference: DF.Literal["Light/Fluid", "Standard/Firm", "Heavy/Resistant"]
    targeted_marketing_optin: DF.Check
    technician_notes: DF.SmallText | None
    workflow_state: DF.Link | None
    # end: auto-generated types

    def autoname(self) -> None:
        """Generate unique player profile ID"""
        if not self.player_profile_id or self.player_profile_id == "New":
            self.player_profile_id = f"PLAYER-{frappe.generate_hash(length=6).upper()}"

    def before_insert(self) -> None:
        """Pre-insert validations and setup"""
        self._validate_required_fields()
        self._validate_email_format()
        self._check_duplicate_email()
        
        if not self.profile_creation_date:
            self.profile_creation_date = today()

    def validate(self) -> None:
        """
        Comprehensive validation before save.
        
        Ensures data integrity, compliance, and business rules.
        """
        self._validate_required_fields()
        self._validate_email_format()
        self._validate_phone_format()
        self._check_coppa_compliance()
        self._validate_equipment_preferences()
        self._validate_instruments_owned()

    def before_save(self) -> None:
        """Pre-save operations"""
        self._sync_instruments_owned()
        self._calc_lifetime_value()
        self._update_last_visit()

    def on_update(self) -> None:
        """Post-update operations"""
        self._sync_email_group()
        self._log_status_changes()

    def on_trash(self) -> None:
        """Pre-delete operations"""
        self._cleanup_references()

    # === VALIDATION METHODS ===

    def _validate_required_fields(self) -> None:
        """Validate all required fields are present"""
        if not self.player_name:
            frappe.throw(_("Full Name is required for Player Profile."))
        if not self.primary_email:
            frappe.throw(_("Primary Email is required for Player Profile."))
        if not self.player_level:
            frappe.throw(_("Player Level is required for Player Profile."))

    def _validate_email_format(self) -> None:
        """Validate email format"""
        if self.primary_email:
            import re

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, self.primary_email):
                frappe.throw(_("Invalid email format: {0}").format(self.primary_email))

    def _validate_phone_format(self) -> None:
        """Validate phone number format if provided"""
        if self.primary_phone:
            import re

            # Remove common phone number formatting characters
            cleaned = re.sub(r"[\s\-\(\)\.]+", "", self.primary_phone)
            # Check if remaining chars are digits and plus (for international)
            if not re.match(r"^[\+]?[\d]+$", cleaned):
                frappe.throw(_("Invalid phone format: {0}").format(self.primary_phone))

    def _check_duplicate_email(self) -> None:
        """Check for duplicate email addresses"""
        if self.primary_email:
            filters = {"primary_email": self.primary_email, "name": ["!=", self.name]}
            if frappe.db.exists("Player Profile", filters):
                frappe.throw(_("A Player Profile with email {0} already exists.").format(self.primary_email))

    def _check_coppa_compliance(self) -> None:
        """
        Ensure COPPA compliance for users under 13.
        
        Automatically disables marketing for minors.
        """
        if hasattr(self, "date_of_birth") and self.date_of_birth:
            try:
                age = (getdate() - getdate(self.date_of_birth)).days // 365
                if age < 13:
                    self.newsletter_subscription = 0
                    self.targeted_marketing_optin = 0
                    self._block_marketing_emails()
            except Exception:
                frappe.log_error(frappe.get_traceback(), "PlayerProfile: COPPA compliance check failed")

    def _validate_equipment_preferences(self) -> None:
        """Validate equipment preferences child table"""
        if self.equipment_preferences:
            for idx, pref in enumerate(self.equipment_preferences, 1):
                if pref.instrument:
                    if not frappe.db.exists("Instrument Profile", pref.instrument):
                        frappe.throw(
                            _("Row {0}: Instrument Profile {1} does not exist").format(
                                idx, pref.instrument
                            )
                        )

    def _validate_instruments_owned(self) -> None:
        """Validate instruments owned child table"""
        if self.instruments_owned:
            seen_serials = set()
            for idx, inst in enumerate(self.instruments_owned, 1):
                serial = inst.get("serial_no")
                if serial:
                    if serial in seen_serials:
                        frappe.throw(_("Row {0}: Duplicate serial number {1}").format(idx, serial))
                    seen_serials.add(serial)

    # === BUSINESS LOGIC METHODS ===

    def _sync_instruments_owned(self) -> None:
        """
        Synchronize instruments_owned table from Instrument Profile links.
        
        ISN-aware: displays human serial even when Instrument holds a Link to ISN.
        """
        try:
            owned = frappe.get_all(
                "Instrument Profile",
                filters={"owner_player": self.name},
                fields=["name", "serial_no", "model", "instrument"],
            )

            self.set("instruments_owned", [])
            for row in owned:
                serial_display = _resolve_serial_display(row)
                self.append(
                    "instruments_owned",
                    {
                        "name": row.get("name"),
                        "serial_no": serial_display,
                        "model": row.get("model"),
                    },
                )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: sync_instruments_owned failed")

    def _calc_lifetime_value(self) -> None:
        """
        Calculate Customer Lifetime Value from linked Sales Invoices.
        
        Sums grand_total from all submitted invoices linked to this player.
        """
        try:
            invoices = frappe.get_all(
                "Sales Invoice",
                filters={"player_profile": self.name, "docstatus": 1},
                fields=["grand_total"],
            )
            self.customer_lifetime_value = sum(inv.get("grand_total", 0) for inv in invoices) if invoices else 0
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: calc_lifetime_value failed")

    def _update_last_visit(self) -> None:
        """Update last visit date from latest service/intake record"""
        try:
            # Check for recent Clarinet Intake records
            latest_intake = frappe.db.get_value(
                "Clarinet Intake",
                filters={"player_profile": self.name},
                fieldname="received_date",
                order_by="received_date desc",
            )
            if latest_intake and (not self.last_visit_date or latest_intake > self.last_visit_date):
                self.last_visit_date = latest_intake
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: update_last_visit failed")

    def _sync_email_group(self) -> None:
        """Sync player to newsletter/marketing email groups based on opt-ins"""
        if not self.primary_email:
            return

        try:
            if self.newsletter_subscription:
                # Add to newsletter group
                if not frappe.db.exists(
                    "Email Group Member", {"email": self.primary_email, "email_group": "Player Newsletter"}
                ):
                    frappe.get_doc(
                        {
                            "doctype": "Email Group Member",
                            "email": self.primary_email,
                            "email_group": "Player Newsletter",
                        }
                    ).insert(ignore_permissions=True, ignore_if_duplicate=True)
            else:
                # Remove from newsletter group
                email_member = frappe.db.get_value(
                    "Email Group Member",
                    {"email": self.primary_email, "email_group": "Player Newsletter"},
                    "name",
                )
                if email_member:
                    frappe.delete_doc("Email Group Member", email_member, ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: sync_email_group failed")

    def _block_marketing_emails(self) -> None:
        """Block marketing emails for COPPA compliance"""
        try:
            if self.primary_email:
                # Unsubscribe from all marketing groups
                email_members = frappe.get_all(
                    "Email Group Member",
                    filters={"email": self.primary_email},
                    fields=["name"],
                )
                for member in email_members:
                    frappe.db.set_value("Email Group Member", member.name, "unsubscribed", 1)

                # Notify parent/guardian if linked customer exists
                customer = frappe.db.get_value(
                    "Customer", {"email_id": self.primary_email}, ["linked_user"], as_dict=True
                )
                if customer and customer.get("linked_user"):
                    parent_email = frappe.db.get_value("User", customer.linked_user, "email")
                    if parent_email:
                        self._send_coppa_notification(parent_email)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: block_marketing_emails failed")

    def _send_coppa_notification(self, parent_email: str) -> None:
        """Send COPPA compliance notification to parent/guardian"""
        try:
            subject = f"Profile Marketing Blocked for {self.player_name}"
            message = f"""
                <p>Dear Parent/Guardian,</p>
                <p>Due to COPPA compliance, marketing emails for <strong>{self.player_name}</strong> 
                have been blocked (age under 13). No action is required.</p>
                <p>Thank you!<br>— The Artisan Clarinets Team</p>
            """
            frappe.sendmail(recipients=[parent_email], subject=subject, message=message)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: send_coppa_notification failed")

    def _log_status_changes(self) -> None:
        """Log significant status changes for audit trail"""
        if self.has_value_changed("profile_status"):
            frappe.logger().info(
                f"Player Profile {self.name} status changed: {self.get_doc_before_save().profile_status} → {self.profile_status}"
            )

    def _cleanup_references(self) -> None:
        """Clean up references before deletion"""
        try:
            # Update instrument profiles
            instruments = frappe.get_all(
                "Instrument Profile", filters={"owner_player": self.name}, fields=["name"]
            )
            for inst in instruments:
                frappe.db.set_value("Instrument Profile", inst.name, "owner_player", "")
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: cleanup_references failed")

    # === WHITELISTED API METHODS ===

    @frappe.whitelist()
    def get_service_history(self) -> list[dict]:
        """
        Get service/repair history for this player.
        
        Returns:
            List of service records with dates and types
        """
        frappe.has_permission("Player Profile", "read", throw=True)

        try:
            history = []

            # Get Clarinet Intake records
            intakes = frappe.get_all(
                "Clarinet Intake",
                filters={"player_profile": self.name},
                fields=["name", "received_date", "workflow_state", "serial_no"],
                order_by="received_date desc",
                limit=50,
            )
            history.extend([{"type": "Intake", **intake} for intake in intakes])

            # Get Repair Orders
            repairs = frappe.get_all(
                "Repair Order",
                filters={"player_profile": self.name},
                fields=["name", "posting_date", "status"],
                order_by="posting_date desc",
                limit=50,
            )
            history.extend([{"type": "Repair", **repair} for repair in repairs])

            # Sort by date
            history.sort(key=lambda x: x.get("received_date") or x.get("posting_date"), reverse=True)

            return history[:50]  # Return top 50
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: get_service_history failed")
            return []

    @frappe.whitelist()
    def get_equipment_recommendations(self) -> dict:
        """
        Generate equipment recommendations based on player level and preferences.
        
        Returns:
            Dict with recommended equipment categories
        """
        frappe.has_permission("Player Profile", "read", throw=True)

        recommendations = {
            "mouthpieces": [],
            "reeds": [],
            "accessories": [],
        }

        # Level-based recommendations
        if self.player_level in ["Student (Beginner)", "Student (Advanced)"]:
            recommendations["mouthpieces"] = ["Vandoren B45", "Vandoren M30"]
            recommendations["reeds"] = ["Vandoren Traditional 2.5-3", "Rico Royal 2.5"]
        elif "Professional" in self.player_level:
            recommendations["mouthpieces"] = ["Vandoren M13 Lyre", "Vandoren BD5"]
            recommendations["reeds"] = ["Vandoren V12 3.5+", "D'Addario Reserve 3.5+"]

        return recommendations

    @frappe.whitelist()
    def update_marketing_preferences(self, newsletter: int, targeted: int) -> dict:
        """
        Update marketing preferences with validation.
        
        Args:
            newsletter: Newsletter subscription flag (0 or 1)
            targeted: Targeted marketing opt-in flag (0 or 1)
            
        Returns:
            Success status
        """
        frappe.has_permission("Player Profile", "write", throw=True)

        try:
            self.newsletter_subscription = int(newsletter)
            self.targeted_marketing_optin = int(targeted)
            self.save()
            return {"success": True, "message": _("Marketing preferences updated successfully")}
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PlayerProfile: update_marketing_preferences failed")
            return {"success": False, "message": _("Failed to update marketing preferences")}
