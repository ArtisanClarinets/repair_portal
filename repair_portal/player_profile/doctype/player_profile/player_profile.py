"""Player Profile DocType controller with Fortune-500 integrations."""

from __future__ import annotations

import re
from datetime import date
from functools import lru_cache
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.query_builder import DocType, functions as fn
from frappe.utils import cint, flt, getdate, nowdate

if TYPE_CHECKING:
    from frappe.types import DF

    from repair_portal.player_profile.doctype.instruments_owned.instruments_owned import (
        InstrumentsOwned,
    )
    from repair_portal.player_profile.doctype.player_equipment_preference.player_equipment_preference import (
        PlayerEquipmentPreference,
    )


PLAYER_NEWSLETTER_GROUP = "Player Newsletter"
PLAYER_PROFILE_SETTINGS = "Player Profile Settings"
CONTACT_LINK = "Contact Link"
INSTRUMENT_PROFILE = "Instrument Profile"
_ALLOWED_PORTAL_FIELDS = {
    "preferred_name",
    "primary_phone",
    "mailing_address_line1",
    "mailing_address_line2",
    "city",
    "state",
    "postal_code",
    "country",
    "communication_preference",
    "newsletter_subscription",
    "targeted_marketing_optin",
}


@lru_cache(maxsize=1)
def _get_settings() -> Optional[Document]:
    """Return Player Profile Settings single doctype as a cached document."""

    try:
        return frappe.get_cached_doc(PLAYER_PROFILE_SETTINGS)
    except frappe.DoesNotExistError:
        return None
    except Exception:
        frappe.log_error(
            title="PlayerProfile Settings Fetch",
            message=frappe.get_traceback(),
        )
        return None


class PlayerProfile(Document):
    """Comprehensive Player Profile controller with validation and integrations."""

    # begin: auto-generated types
    affiliation: DF.Data | None
    city: DF.Data | None
    communication_preference: DF.Literal["Email", "SMS", "Phone Call"] | None
    country: DF.Link | None
    customer: DF.Link | None
    customer_lifetime_value: DF.Currency
    date_of_birth: DF.Date | None
    instruments_owned: DF.Table[InstrumentsOwned]
    intonation_notes: DF.SmallText | None
    last_visit_date: DF.Date | None
    mailing_address_line1: DF.Data | None
    mailing_address_line2: DF.Data | None
    newsletter_subscription: DF.Check
    player_equipment_preferences: DF.Table[PlayerEquipmentPreference]
    player_level: DF.Literal[
        "Student (Beginner)",
        "Student (Intermediate)",
        "Student (Advanced)",
        "University Student",
        "Amateur/Hobbyist",
        "Professional (Orchestral)",
        "Professional (Jazz/Commercial)",
        "Educator",
        "Collector",
    ]
    player_name: DF.Data
    player_profile_id: DF.Data
    postal_code: DF.Data | None
    preferred_name: DF.Data | None
    primary_email: DF.Data
    primary_phone: DF.Data
    primary_playing_styles: DF.SmallText | None
    primary_teacher: DF.Data | None
    profile_creation_date: DF.Date | None
    profile_status: DF.Literal["Draft", "Active", "Archived"]
    referral_source: DF.Data | None
    state: DF.Data | None
    targeted_marketing_optin: DF.Check
    technician_notes: DF.SmallText | None
    # end: auto-generated types

    def autoname(self) -> None:
        """Generate deterministic autoname and mirror to player_profile_id."""

        naming_series = self.naming_series or "PLAYER-.####"  # type: ignore[attr-defined]
        if not self.name or self.name == "New Player Profile 1":
            self.name = make_autoname(naming_series)
        if not self.player_profile_id:
            self.player_profile_id = self.name

    def before_insert(self) -> None:
        """Perform required validation before insertion."""

        self._validate_required_fields()
        self._validate_email_format()
        self._validate_phone_format()
        self._check_duplicate_email()
        self._validate_customer_link()
        self.profile_creation_date = self.profile_creation_date or nowdate()
        self.player_profile_id = self.player_profile_id or self.name

    def validate(self) -> None:
        """Run validation on each save."""

        self._validate_required_fields()
        self._validate_email_format()
        self._validate_phone_format()
        self._check_duplicate_email()
        self._validate_customer_link()
        self._validate_equipment_preferences()
        self._validate_instruments_owned()
        self._enforce_archived_read_only()
        self._apply_coppa_rules()

    def before_save(self) -> None:
        """Refresh derived metrics prior to save."""

        self.player_profile_id = self.player_profile_id or self.name
        self._sync_instruments_owned()
        self._calculate_clv()
        self._update_last_visit_date()

    def on_update(self) -> None:
        """Handle integrations after document is updated."""

        self._sync_email_group()
        self._log_status_changes()

    def on_trash(self) -> None:
        """Clean downstream references prior to deletion."""

        self._cleanup_references()

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def _validate_required_fields(self) -> None:
        required_fields = {
            "player_name": self.player_name,
            "primary_email": self.primary_email,
            "primary_phone": self.primary_phone,
            "player_level": self.player_level,
        }
        missing = [label for label, value in required_fields.items() if not value]
        if missing:
            frappe.throw(_("Missing required fields: {0}").format(", ".join(missing)))

    def _validate_email_format(self) -> None:
        if not self.primary_email:
            return
        email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
        if not email_pattern.fullmatch(self.primary_email.strip()):
            frappe.throw(_("Invalid email format: {0}").format(self.primary_email))

    def _validate_phone_format(self) -> None:
        if not self.primary_phone:
            return
        phone_pattern = re.compile(r"^[0-9+()\-\s]{7,20}$")
        if not phone_pattern.fullmatch(self.primary_phone.strip()):
            frappe.throw(_("Invalid phone number format: {0}").format(self.primary_phone))

    def _check_duplicate_email(self) -> None:
        if not self.primary_email:
            return
        email_value = self.primary_email.strip().lower()
        profile = DocType("Player Profile")
        try:
            result = (
                frappe.qb.from_(profile)
                .select(profile.name)
                .where(fn.Lower(profile.primary_email) == email_value)
                .where(profile.name != (self.name or ""))
                .limit(1)
            ).run()
        except Exception:
            frappe.log_error(title="PlayerProfile Duplicate Email", message=frappe.get_traceback())
            result = []
        if result:
            frappe.throw(_("A player profile already exists for email {0}").format(self.primary_email))

    def _validate_customer_link(self) -> None:
        if self.customer and not frappe.db.exists("Customer", self.customer):
            frappe.throw(_("Customer {0} does not exist").format(self.customer))

    def _validate_equipment_preferences(self) -> None:
        for idx, row in enumerate(self.player_equipment_preferences or [], start=1):
            if row.instrument and not frappe.db.exists("Instrument Profile", row.instrument):
                frappe.throw(_("Row {0}: Instrument Profile {1} not found").format(idx, row.instrument))

    def _validate_instruments_owned(self) -> None:
        seen_profiles: set[str] = set()
        for idx, row in enumerate(self.instruments_owned or [], start=1):
            if not row.customer:
                frappe.throw(_("Row {0}: Customer is required for owned instruments").format(idx))
            if self.customer and row.customer != self.customer:
                frappe.throw(
                    _("Row {0}: Customer must match profile customer {1}").format(idx, self.customer)
                )
            if row.instrument_profile:
                if row.instrument_profile in seen_profiles:
                    frappe.throw(
                        _("Row {0}: Duplicate instrument profile {1}").format(idx, row.instrument_profile)
                    )
                seen_profiles.add(row.instrument_profile)
                if not frappe.db.exists("Instrument Profile", row.instrument_profile):
                    frappe.throw(
                        _("Row {0}: Instrument Profile {1} not found").format(idx, row.instrument_profile)
                    )
            if row.instrument and not frappe.db.exists("Instrument", row.instrument):
                frappe.throw(_("Row {0}: Instrument {1} not found").format(idx, row.instrument))

    def _enforce_archived_read_only(self) -> None:
        if not self.name or self.is_new():
            return
        previous = self.get_doc_before_save()  # type: ignore[assignment]
        if not previous:
            return
        if previous.profile_status == "Archived" and self.profile_status == "Archived":
            changed_fields = self.get_dirty_fields()  # type: ignore[attr-defined]
            if changed_fields:
                frappe.throw(_("Archived player profiles are read-only. Use Restore to modify."))

    def _apply_coppa_rules(self) -> None:
        if not self.date_of_birth:
            return
        try:
            birth_date = getdate(self.date_of_birth)
        except Exception:
            frappe.log_error(
                title="PlayerProfile Invalid DOB",
                message=frappe.get_traceback(),
            )
            return
        today = getdate()
        age_years = (today - birth_date).days // 365 if birth_date else 0
        self.flags.coppa_restricted = age_years < 13
        if age_years < 13:
            if self.newsletter_subscription:
                self.newsletter_subscription = 0
            if self.targeted_marketing_optin:
                self.targeted_marketing_optin = 0
            self._block_marketing_emails()
            if not getattr(self.flags, "coppa_noted", False):
                self.add_comment(
                    "Comment",
                    _("Marketing communication disabled automatically due to COPPA requirements."),
                )
                self.flags.coppa_noted = True
        else:
            self.flags.coppa_noted = False

    # ------------------------------------------------------------------
    # Derived data helpers
    # ------------------------------------------------------------------
    def _sync_instruments_owned(self) -> None:
        if not frappe.db.has_column(INSTRUMENT_PROFILE, "owner_player"):
            return
        try:
            rows = frappe.get_all(
                INSTRUMENT_PROFILE,
                filters={"owner_player": self.name},
                fields=["name", "instrument", "serial_no", "model", "customer"],
            )
        except Exception:
            frappe.log_error(
                title="PlayerProfile Instrument Sync",
                message=frappe.get_traceback(),
            )
            return

        if rows is None:
            rows = []

        self.set("instruments_owned", [])
        for row in rows:
            serial_display = self._resolve_serial_display(row)
            self.append(
                "instruments_owned",
                {
                    "instrument_profile": row.get("name"),
                    "instrument": row.get("instrument"),
                    "serial_number": serial_display,
                    "model": row.get("model"),
                    "customer": row.get("customer") or self.customer,
                },
            )

    def _calculate_clv(self) -> None:
        invoice = DocType("Sales Invoice")
        try:
            result = (
                frappe.qb.from_(invoice)
                .select(fn.Coalesce(fn.Sum(invoice.grand_total), 0))
                .where(invoice.player_profile == self.name)
                .where(invoice.docstatus == 1)
            ).run()
            total = flt(result[0][0]) if result else 0.0
            self.customer_lifetime_value = total
        except Exception:
            frappe.log_error(
                title="PlayerProfile CLV",
                message=frappe.get_traceback(),
            )
            self.customer_lifetime_value = 0.0

    def _update_last_visit_date(self) -> None:
        latest_dates: List[date] = []
        try:
            intake_date = frappe.db.get_value(
                "Clarinet Intake",
                {"player_profile": self.name},
                "received_date",
                order_by="received_date desc",
            )
            if intake_date:
                latest_dates.append(getdate(intake_date))
        except Exception:
            frappe.log_error(title="PlayerProfile Last Visit", message=frappe.get_traceback())

        try:
            repair_date = frappe.db.get_value(
                "Repair Order",
                {"player_profile": self.name},
                "posting_date",
                order_by="posting_date desc",
            )
            if repair_date:
                latest_dates.append(getdate(repair_date))
        except Exception:
            frappe.log_error(title="PlayerProfile Last Visit", message=frappe.get_traceback())

        if latest_dates:
            self.last_visit_date = max(latest_dates)

    def _sync_email_group(self) -> None:
        if not self.primary_email:
            return

        group_name = self._resolve_email_group_name()
        if not group_name:
            return

        try:
            existing_member = frappe.db.get_value(
                "Email Group Member",
                {"email": self.primary_email, "email_group": group_name},
                "name",
            )
            if getattr(self.flags, "coppa_restricted", False):
                if existing_member:
                    frappe.delete_doc("Email Group Member", existing_member, ignore_permissions=True)
                return
            if self.newsletter_subscription:
                if not existing_member:
                    frappe.get_doc(
                        {
                            "doctype": "Email Group Member",
                            "email": self.primary_email,
                            "email_group": group_name,
                        }
                    ).insert(ignore_permissions=True, ignore_if_duplicate=True)
            elif existing_member:
                frappe.delete_doc("Email Group Member", existing_member, ignore_permissions=True)
        except Exception:
            frappe.log_error(title="PlayerProfile Email Group", message=frappe.get_traceback())

    def _log_status_changes(self) -> None:
        if not self.has_value_changed("profile_status"):
            return
        previous = ""  # default when inserted
        try:
            before = self.get_doc_before_save()
            previous = getattr(before, "profile_status", "") if before else ""
        except Exception:
            pass
        message = _("Profile status changed from {0} to {1}").format(previous or "—", self.profile_status)
        self.add_comment("Comment", message)

    def _cleanup_references(self) -> None:
        try:
            group_name = self._resolve_email_group_name()
            if group_name and self.primary_email:
                member = frappe.db.get_value(
                    "Email Group Member",
                    {"email": self.primary_email, "email_group": group_name},
                    "name",
                )
                if member:
                    frappe.delete_doc("Email Group Member", member, ignore_permissions=True)
        except Exception:
            frappe.log_error(title="PlayerProfile Cleanup Email", message=frappe.get_traceback())

        try:
            instruments = frappe.get_all(
                INSTRUMENT_PROFILE,
                filters={"owner_player": self.name},
                pluck="name",
            ) if frappe.db.has_column(INSTRUMENT_PROFILE, "owner_player") else []
            for instrument in instruments:
                frappe.db.set_value(INSTRUMENT_PROFILE, instrument, "owner_player", "")
        except Exception:
            frappe.log_error(title="PlayerProfile Cleanup Instruments", message=frappe.get_traceback())

        try:
            if frappe.db.exists("DocType", CONTACT_LINK):
                frappe.db.delete(CONTACT_LINK, {"link_doctype": "Player Profile", "link_name": self.name})
        except Exception:
            frappe.log_error(title="PlayerProfile Cleanup Contacts", message=frappe.get_traceback())

    # ------------------------------------------------------------------
    # Marketing helpers
    # ------------------------------------------------------------------
    def _block_marketing_emails(self) -> None:
        if not self.primary_email:
            return
        try:
            members = frappe.get_all(
                "Email Group Member",
                filters={"email": self.primary_email},
                fields=["name"],
            )
            for member in members:
                frappe.db.set_value("Email Group Member", member.name, "unsubscribed", 1)
            group_name = self._resolve_email_group_name()
            if group_name:
                member_name = frappe.db.get_value(
                    "Email Group Member",
                    {"email": self.primary_email, "email_group": group_name},
                    "name",
                )
                if member_name:
                    frappe.delete_doc("Email Group Member", member_name, ignore_permissions=True)
        except Exception:
            frappe.log_error(title="PlayerProfile Block Marketing", message=frappe.get_traceback())

    def _resolve_email_group_name(self) -> Optional[str]:
        configured = None
        settings = _get_settings()
        if settings and getattr(settings, "newsletter_email_group", None):
            configured = settings.newsletter_email_group
        candidate = configured or PLAYER_NEWSLETTER_GROUP
        if frappe.db.exists("Email Group", candidate):
            return candidate
        alternate = frappe.db.get_value("Email Group", {"title": candidate}, "name")
        if alternate:
            return alternate
        try:
            doc = frappe.get_doc(
                {
                    "doctype": "Email Group",
                    "title": candidate,
                }
            ).insert(ignore_permissions=True)
            return doc.name
        except Exception:
            frappe.log_error(title="PlayerProfile Email Group Seed", message=frappe.get_traceback())
        return None

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _resolve_serial_display(row: Dict[str, Any]) -> Optional[str]:
        serial = row.get("serial_no") or row.get("serial_number")
        if serial:
            return serial
        instrument = row.get("instrument")
        if not instrument:
            return None
        try:
            value = frappe.db.get_value("Instrument", instrument, "serial_no")
            return value
        except Exception:
            frappe.log_error(title="PlayerProfile Serial", message=frappe.get_traceback())
            return None

    # ------------------------------------------------------------------
    # Contact helpers
    # ------------------------------------------------------------------
    def sync_contact(self, force: bool = False) -> Optional[str]:
        """Create or update a Contact linked to this Player Profile and Customer."""

        if not self.customer:
            frappe.throw(_("Link a Customer before syncing contacts."))

        contact_name: Optional[str] = None
        try:
            contact_name = frappe.db.get_value(
                CONTACT_LINK,
                {"link_doctype": "Player Profile", "link_name": self.name},
                "parent",
            )
        except Exception:
            frappe.log_error(title="PlayerProfile Contact Lookup", message=frappe.get_traceback())

        contact_doc: Optional[Document] = None
        if contact_name:
            try:
                contact_doc = frappe.get_doc("Contact", contact_name)
            except Exception:
                contact_doc = None

        if not contact_doc and self.primary_email:
            try:
                lookup = frappe.db.get_value(
                    "Contact",
                    {"email_id": self.primary_email},
                    "name",
                )
                if lookup:
                    contact_doc = frappe.get_doc("Contact", lookup)
            except Exception:
                contact_doc = None

        if not contact_doc and not force and contact_name:
            try:
                contact_doc = frappe.get_doc("Contact", contact_name)
            except Exception:
                contact_doc = None

        if not contact_doc:
            contact_doc = frappe.new_doc("Contact")

        preferred = (self.preferred_name or self.player_name or "Player").strip()
        first_name = preferred.split(" ", 1)[0] if preferred else "Player"
        last_name = preferred.split(" ", 1)[1] if " " in preferred else None

        contact_doc.first_name = first_name
        if last_name:
            contact_doc.last_name = last_name
        contact_doc.email_id = self.primary_email or contact_doc.email_id
        if self.primary_phone:
            contact_doc.phone = self.primary_phone
            contact_doc.mobile_no = self.primary_phone

        existing_links: set[tuple[str, str]] = set()
        for link in (contact_doc.links or []):
            existing_links.add((link.link_doctype, link.link_name))

        def ensure_link(doctype: str, name: str) -> None:
            if not name:
                return
            if (doctype, name) in existing_links:
                return
            contact_doc.append("links", {"link_doctype": doctype, "link_name": name})
            existing_links.add((doctype, name))

        ensure_link("Customer", self.customer)
        ensure_link("Player Profile", self.name)

        try:
            contact_doc.save(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            frappe.log_error(title="PlayerProfile Contact Sync", message=frappe.get_traceback())
            return None

        return contact_doc.name


# ----------------------------------------------------------------------
# Whitelisted APIs
# ----------------------------------------------------------------------


def _ensure_profile_permission(
    doc: PlayerProfile, action: str = "read", *, allow_portal_self: bool = False
) -> None:
    if doc.has_permission(action):
        return

    if allow_portal_self:
        session_email = frappe.db.get_value("User", frappe.session.user, "email")
        if session_email and session_email.lower() == (doc.primary_email or "").lower():
            return

    frappe.throw(
        _("Insufficient permission to {0} Player Profile").format(action), frappe.PermissionError
    )


@frappe.whitelist()
def get(player_email: Optional[str] = None) -> Dict[str, Any]:
    """Fetch a player profile by email with permission enforcement."""

    if not player_email:
        player_email = frappe.db.get_value("User", frappe.session.user, "email")
    if not player_email:
        frappe.throw(_("An email address is required to locate the profile."))

    docname = frappe.db.get_value("Player Profile", {"primary_email": player_email}, "name")
    if not docname:
        frappe.throw(_("No player profile found for email {0}").format(player_email), frappe.DoesNotExistError)

    doc = frappe.get_doc("Player Profile", docname)
    _ensure_profile_permission(doc, "read", allow_portal_self=True)
    return doc.as_dict(no_nulls=True)


@frappe.whitelist()
def save(doc_json: str) -> Dict[str, Any]:
    """Save updates to a Player Profile enforcing field-level rules for portal users."""

    payload = frappe.parse_json(doc_json)
    if not isinstance(payload, dict):
        frappe.throw(_("Invalid payload for Player Profile update."))

    docname = payload.get("name")
    if not docname:
        frappe.throw(_("Document name is required."))

    doc: PlayerProfile = frappe.get_doc("Player Profile", docname)  # type: ignore[assignment]
    roles = set(frappe.get_roles(frappe.session.user))
    desk_roles = {"System Manager", "Repair Manager", "Technician"}
    is_portal_user = not bool(roles & desk_roles)

    session_email = frappe.db.get_value("User", frappe.session.user, "email")
    if is_portal_user:
        if session_email and session_email.lower() != (doc.primary_email or "").lower():
            frappe.throw(_("You can only update your own player profile."), frappe.PermissionError)
        disallowed = set(payload.keys()) - ({"doctype", "name"} | _ALLOWED_PORTAL_FIELDS)
        if disallowed:
            frappe.throw(_("Portal users cannot update fields: {0}").format(", ".join(sorted(disallowed))))

    save_kwargs: Dict[str, Any] = {}

    if is_portal_user:
        _ensure_profile_permission(doc, "read", allow_portal_self=True)
        save_kwargs["ignore_permissions"] = True
    else:
        _ensure_profile_permission(doc, "write")

    for field, value in payload.items():
        if field in {"doctype", "name"}:
            continue
        if is_portal_user and field not in _ALLOWED_PORTAL_FIELDS:
            continue
        if field in {"newsletter_subscription", "targeted_marketing_optin"}:
            doc.set(field, cint(value))
        else:
            doc.set(field, value)

    doc.save(**save_kwargs)
    return {"name": doc.name, "player_profile_id": doc.player_profile_id}


@frappe.whitelist()
def get_service_history(player_profile: str) -> List[Dict[str, Any]]:
    """Return recent intake and repair activity for a player profile."""

    if not player_profile:
        frappe.throw(_("Player Profile is required."))
    doc = frappe.get_doc("Player Profile", player_profile)
    _ensure_profile_permission(doc, "read")

    history: List[Dict[str, Any]] = []
    try:
        intakes = frappe.get_all(
            "Clarinet Intake",
            filters={"player_profile": player_profile},
            fields=["name", "received_date", "serial_no", "status"],
            order_by="received_date desc",
            limit=20,
        )
        for intake in intakes:
            history.append(
                {
                    "date": intake.get("received_date"),
                    "type": "Clarinet Intake",
                    "reference": intake.get("name"),
                    "serial_number": intake.get("serial_no"),
                    "description": intake.get("status"),
                }
            )
    except Exception:
        frappe.log_error(title="PlayerProfile Service History", message=frappe.get_traceback())

    try:
        repairs = frappe.get_all(
            "Repair Order",
            filters={"player_profile": player_profile},
            fields=["name", "posting_date", "status", "serial_no"],
            order_by="posting_date desc",
            limit=20,
        )
        for repair in repairs:
            history.append(
                {
                    "date": repair.get("posting_date"),
                    "type": "Repair Order",
                    "reference": repair.get("name"),
                    "serial_number": repair.get("serial_no"),
                    "description": repair.get("status"),
                }
            )
    except Exception:
        frappe.log_error(title="PlayerProfile Service History", message=frappe.get_traceback())

    history.sort(key=lambda row: row.get("date") or date.min, reverse=True)
    return history


@frappe.whitelist()
def update_marketing_preferences(
    name: str,
    newsletter: Optional[int | str] = None,
    targeted: Optional[int | str] = None,
) -> Dict[str, Any]:
    """Update marketing opt-ins with COPPA safeguards."""

    if not name:
        frappe.throw(_("Player Profile name is required."))
    doc: PlayerProfile = frappe.get_doc("Player Profile", name)  # type: ignore[assignment]
    _ensure_profile_permission(doc, "write")

    if newsletter is not None:
        doc.newsletter_subscription = cint(newsletter)
    if targeted is not None:
        doc.targeted_marketing_optin = cint(targeted)

    doc._apply_coppa_rules()
    doc.save()

    return {
        "name": doc.name,
        "newsletter_subscription": cint(doc.newsletter_subscription),
        "targeted_marketing_optin": cint(doc.targeted_marketing_optin),
    }


@frappe.whitelist()
def sync_contact(name: str, force: int | str = 0) -> Dict[str, Any]:
    """Ensure a Contact exists for the Player Profile linked to its Customer."""

    if not name:
        frappe.throw(_("Player Profile name is required."))

    doc: PlayerProfile = frappe.get_doc("Player Profile", name)  # type: ignore[assignment]
    _ensure_profile_permission(doc, "write")

    contact_name = doc.sync_contact(force=bool(cint(force)))
    if not contact_name:
        frappe.throw(_("Contact sync failed; review the error log for details."))

    return {"name": doc.name, "contact": contact_name}
