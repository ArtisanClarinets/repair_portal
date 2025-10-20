# Path: repair_portal/repair_portal/customer/doctype/linked_players/linked_players.py
# Date: 2025-01-27
# Version: 3.0.0
# Description: Child table for linking customers to player profiles with relationship management and validation
# Dependencies: frappe.model.document, Person, Player Profile, Customer

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, getdate, nowdate


class LinkedPlayers(Document):
    """
    Child table for linking customers to player profiles.

    Manages customer-player relationships with validation, primary designation,
    and comprehensive relationship tracking capabilities.
    """

    def validate(self) -> None:
        """Validate linked player record"""
        try:
            self._validate_required_fields()
            self._validate_links_exist()
            self._validate_unique_per_parent()
            self._enforce_single_primary()
            self._normalize_dates()
            self._validate_relationship_type()
        except frappe.ValidationError:
            raise
        except Exception as exc:
            frappe.log_error(frappe.get_traceback(), f"[LinkedPlayers.validate] {repr(exc)}")
            frappe.throw(_("Unexpected error while validating Linked Player. Please contact support."))

    def before_save(self) -> None:
        """Pre-save operations"""
        self._sync_player_details()
        self._update_audit_fields()

    def on_update(self) -> None:
        """Post-update operations"""
        self._update_player_profile_link()
        self._log_relationship_change()

    def before_delete(self) -> None:
        """Pre-delete operations"""
        self._handle_primary_deletion()
        self._clean_player_profile_link()

    def _validate_required_fields(self) -> None:
        """Validate required fields"""
        if not self.player_profile:
            frappe.throw(_("Player Profile is required"))

        if not self.customer:
            frappe.throw(_("Customer is required"))

        if not self.relationship:
            frappe.throw(_("Relationship type is required"))

    def _validate_links_exist(self) -> None:
        """Confirm both linked doctypes exist and are active"""
        missing = []

        # Validate Customer exists and is active
        customer_exists = frappe.db.get_value("Customer", self.customer, ["name", "disabled"], as_dict=True)
        if not customer_exists:
            missing.append(f"Customer: {self.customer}")
        elif customer_exists.disabled:
            missing.append(f"Customer: {self.customer} (disabled)")

        # Validate Player Profile exists
        player_exists = frappe.db.get_value("Player Profile", self.player_profile, "name")
        if not player_exists:
            missing.append(f"Player Profile: {self.player_profile}")

        if missing:
            frappe.throw(_("Linked document(s) not found or inactive: {0}").format(", ".join(missing)))

    def _validate_unique_per_parent(self) -> None:
        """Prevent duplicate Player Profile links in the same parent document"""
        if not self.parentfield:
            return  # Safety-net for orphaned rows

        siblings = self.get_siblings() if hasattr(self, "get_siblings") else []
        duplicates = [d for d in siblings if d.player_profile == self.player_profile and d.name != self.name]

        if duplicates:
            frappe.throw(_("This Player Profile is already linked to the current Customer"))

    def _enforce_single_primary(self) -> None:
        """Ensure only one row per parent is flagged as primary"""
        if not cint(self.is_primary):
            return

        siblings = self.get_siblings() if hasattr(self, "get_siblings") else []
        primaries = [d for d in siblings if cint(d.is_primary) and d.name != self.name]

        if primaries:
            frappe.throw(_("Only one Player Profile may be marked as Primary per Customer"))

    def _validate_relationship_type(self) -> None:
        """Validate relationship type against allowed values"""
        allowed_relationships = [
            "Self",
            "Parent",
            "Guardian",
            "Teacher",
            "Student",
            "Family Member",
            "Friend",
            "Other",
        ]

        if self.relationship not in allowed_relationships:
            frappe.throw(_("Invalid relationship type: {0}").format(self.relationship))

    def _normalize_dates(self) -> None:
        """Guarantee date_linked is set and valid"""
        if not self.date_linked:
            self.date_linked = nowdate()
        else:
            try:
                self.date_linked = getdate(self.date_linked)
            except Exception:
                frappe.throw(_("Invalid date format for Date Linked"))

    def _sync_player_details(self) -> None:
        """Sync player details for display purposes"""
        if self.player_profile:
            player_details = frappe.db.get_value(
                "Player Profile",
                self.player_profile,
                ["player_name", "instrument_category", "skill_level"],
                as_dict=True,
            )
            if player_details:
                self.player_name = player_details.player_name
                self.instrument_category = player_details.instrument_category
                self.skill_level = player_details.skill_level

        if self.person:
            person_details = frappe.db.get_value(
                "Person", self.person, ["first_name", "last_name", "email", "mobile_no"], as_dict=True
            )
            if person_details:
                full_name = " ".join(filter(None, [person_details.first_name, person_details.last_name]))
                self.person_name = full_name
                self.contact_email = person_details.email
                self.contact_mobile = person_details.mobile_no

    def _update_audit_fields(self) -> None:
        """Update audit fields"""
        if self.is_new():
            self.created_by = frappe.session.user
            self.creation_date = nowdate()
        else:
            self.modified_by = frappe.session.user
            self.modified_date = nowdate()

    def _update_player_profile_link(self) -> None:
        """Update player profile with customer link"""
        if self.player_profile and self.parent:
            try:
                player_doc = frappe.get_doc("Player Profile", self.player_profile)
                if not player_doc.linked_customer:
                    player_doc.linked_customer = self.parent
                    player_doc.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Failed to update player profile link: {str(e)}")

    def _handle_primary_deletion(self) -> None:
        """Handle deletion of primary player"""
        if cint(self.is_primary):
            # Set another player as primary if available
            siblings = self.get_siblings() if hasattr(self, "get_siblings") else []
            other_players = [d for d in siblings if d.name != self.name]

            if other_players:
                # Set the first one as primary
                other_players[0].is_primary = 1
                frappe.msgprint(_("Another player has been set as primary"))

    def _clean_player_profile_link(self) -> None:
        """Clean customer link from player profile when deleting"""
        if self.player_profile:
            try:
                player_doc = frappe.get_doc("Player Profile", self.player_profile)
                if player_doc.linked_customer == self.parent:
                    player_doc.linked_customer = ""
                    player_doc.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"Failed to clean player profile link: {str(e)}")

    def _log_relationship_change(self) -> None:
        """Log relationship changes for audit trail"""
        if self.has_value_changed("is_primary") and self.is_primary:
            frappe.logger().info(f"Player {self.player_profile} set as primary for customer {self.parent}")

        if self.has_value_changed("relationship"):
            frappe.logger().info(
                f"Relationship changed for player {self.player_profile} "
                f"to customer {self.parent}: {self.relationship}"
            )

    @frappe.whitelist()
    def get_player_details(self) -> dict[str, any]:
        """Get comprehensive player details"""
        if not self.player_profile:
            return {}

        player_doc = frappe.get_doc("Player Profile", self.player_profile)
        return {
            "player_name": player_doc.player_name,
            "instrument_category": player_doc.instrument_category,
            "skill_level": player_doc.skill_level,
            "date_of_birth": player_doc.date_of_birth,
            "workflow_state": player_doc.workflow_state,
            "instruments_owned": len(player_doc.instruments_owned or []),
            "performance_history": len(player_doc.performance_history or []),
            "last_updated": player_doc.modified,
        }

    @frappe.whitelist()
    def get_relationship_history(self) -> list[dict]:
        """Get relationship history for this player-customer link"""
        # This could be expanded to track relationship changes over time
        return [
            {
                "date": self.date_linked,
                "relationship": self.relationship,
                "is_primary": self.is_primary,
                "notes": self.notes,
            }
        ]

    def as_dict_safe(self) -> dict[str, any]:
        """Return a sanitized dict excluding private meta fields"""
        public_fields = {
            "person",
            "person_name",
            "player_profile",
            "player_name",
            "relationship",
            "date_linked",
            "is_primary",
            "notes",
            "instrument_category",
            "skill_level",
            "contact_email",
            "contact_mobile",
        }
        return {k: v for k, v in self.as_dict().items() if k in public_fields}

    @staticmethod
    @frappe.whitelist()
    def get_available_players(customer: str) -> list[dict]:
        """Get list of available players not yet linked to customer"""
        # Get already linked players
        linked_players = frappe.db.get_list(
            "Linked Players",
            filters={"parent": customer, "parenttype": "Customer"},
            fields=["player_profile"],
        )
        linked_player_ids = [p.player_profile for p in linked_players]

        # Get available players
        filters = {"workflow_state": ["!=", "Archived"]}
        if linked_player_ids:
            filters["name"] = ["not in", linked_player_ids]

        return frappe.db.get_list(
            "Player Profile",
            filters=filters,
            fields=["name", "player_name", "instrument_category", "skill_level"],
            order_by="player_name",
        )
