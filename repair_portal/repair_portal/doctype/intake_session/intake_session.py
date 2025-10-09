"""Intake Session DocType controller."""

from __future__ import annotations

from datetime import date
from typing import Any

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, now, today

_PRIVILEGED_ROLES = {"System Manager", "Intake Coordinator"}


def _is_privileged(user: str | None = None) -> bool:
    user = user or frappe.session.user
    if not user:
        return False
    if user == "Administrator":
        return True
    roles = set(frappe.get_roles(user))
    return bool(roles.intersection(_PRIVILEGED_ROLES))


def _get_session_ttl_days() -> int:
    """Return the configured TTL in days for intake sessions (default 14)."""

    conf_value = None
    if getattr(frappe.local, "conf", None):
        conf_value = frappe.local.conf.get("intake_session_ttl_days")
    if conf_value is not None:
        try:
            return max(1, int(conf_value))
        except (TypeError, ValueError):
            frappe.log_error(
                title="Intake Session TTL Config Error",
                message=f"Invalid intake_session_ttl_days in site_config: {conf_value}",
            )

    try:
        single_value = frappe.db.get_single_value(
            "Repair Portal Settings", "intake_session_ttl_days"
        )
        if single_value:
            return max(1, int(single_value))
    except Exception:
        frappe.log_error(
            title="Intake Session TTL Fetch Error",
            message=frappe.get_traceback(),
        )

    return 14


def _ensure_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    if value:
        return frappe.utils.getdate(value)
    return frappe.utils.getdate(today())


def _load_json(value: Any) -> dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    try:
        parsed = frappe.parse_json(value)
    except Exception:
        return {}
    return parsed or {}


class IntakeSession(Document):
    """Store resumable intake wizard sessions and telemetry."""

    def before_insert(self) -> None:
        self._ensure_session_id()
        self._stamp_created_by()
        self._set_expiry_if_missing()

    def validate(self) -> None:
        self._stamp_created_by()
        self._ensure_session_id()
        self._set_expiry_if_missing()
        self._enforce_ownership()

    def before_save(self) -> None:
        self._enforce_ownership()

    def _ensure_session_id(self) -> None:
        if self.session_id:
            return
        random_hash = frappe.generate_hash(length=8).upper()
        self.session_id = f"ISN-{random_hash}"
        self.name = self.session_id

    def _stamp_created_by(self) -> None:
        if not self.created_by:
            self.created_by = frappe.session.user
        if not self.name:
            self.name = self.session_id or self.created_by

    def _set_expiry_if_missing(self) -> None:
        ttl_days = _get_session_ttl_days()
        if not self.expires_on:
            self.expires_on = add_days(today(), ttl_days)
        else:
            expires = _ensure_date(self.expires_on)
            minimum = add_days(today(), 1)
            if expires < minimum:
                self.expires_on = add_days(today(), ttl_days)

    def _enforce_ownership(self) -> None:
        if not self.created_by:
            return
        if self.status not in {"Draft", "Abandoned"}:
            return
        user = frappe.session.user
        if user == self.created_by:
            return
        if _is_privileged(user):
            return
        frappe.throw(_("You do not have permission to modify this intake session."), frappe.PermissionError)

    def append_event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        """Append a telemetry event to intake_json.events with timestamp."""

        payload = payload or {}
        data = _load_json(self.intake_json)
        events = data.get("events") or []
        if not isinstance(events, list):
            events = []
        events.append(
            {
                "type": event_type,
                "timestamp": now(),
                "payload": payload,
            }
        )
        data["events"] = events
        self.intake_json = data


def get_permission_query_conditions(user: str) -> str:
    if _is_privileged(user):
        return ""
    user = frappe.db.escape(user)
    return f"(`tabIntake Session`.created_by = {user})"


def has_permission(doc: IntakeSession, ptype: str, user: str) -> bool:
    if ptype in {"read", "write", "delete", "submit", "cancel"}:
        if user == doc.created_by:
            return True
        if _is_privileged(user):
            return True
        if ptype == "read" and doc.status == "Submitted":
            return True
        return False
    return True
