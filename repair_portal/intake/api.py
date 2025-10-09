
# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/api.py
# Last Updated: 2025-10-10
# Version: v2.0.0 (Intake wizard APIs, ownership enforcement, telemetry logging)
# Purpose:
#   Hardened API surface for the Intake wizard and supporting flows.
#   • Secure endpoints for lookup, upserts, session persistence, and intake submission
#   • Strict allow_guest=False with role/permission validation and telemetry logging
#   • Reuse existing intake services (serial utilities, customer sync, brand mapping)

from __future__ import annotations

from typing import Any, Sequence
from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import get_link_to_form

from repair_portal.intake.doctype.brand_mapping_rule.brand_mapping_rule import map_brand
from repair_portal.intake.services import intake_sync
from repair_portal.repair_portal_settings.doctype.repair_portal_settings.repair_portal_settings import (  # noqa: F401
    RepairPortalSettings,
)
from repair_portal.utils.serials import find_by_serial, normalize_serial

LOGGER = frappe.logger("intake")
_PRIVILEGED_ROLES = {"System Manager", "Intake Coordinator"}
_ALLOWED_PLAYER_FIELDS = {
    "player_name",
    "preferred_name",
    "primary_email",
    "primary_phone",
    "player_level",
    "customer",
    "newsletter_subscription",
    "targeted_marketing_optin",
    "player_profile_id",
}



def _ensure_serial_field_type() -> str | None:
    try:
        df = frappe.get_meta("Instrument").get_field("serial_no")
    except Exception:
        return None
    return getattr(df, "fieldtype", None) if df else None


def _is_privileged(user: str | None = None) -> bool:
    user = user or frappe.session.user
    if not user:
        return False
    if user == "Administrator":
        return True
    return bool(set(frappe.get_roles(user)).intersection(_PRIVILEGED_ROLES))


def _ensure_intake_permission(ptype: str = "read") -> None:
    if frappe.has_permission("Clarinet Intake", ptype=ptype):
        return
    if _is_privileged():
        return
    frappe.throw(_("Not permitted"), frappe.PermissionError)


def _ensure_player_permission(ptype: str = "write") -> None:
    if frappe.has_permission("Player Profile", ptype=ptype):
        return
    if _is_privileged():
        return
    frappe.throw(_("Not permitted"), frappe.PermissionError)


def _ensure_customer_permission(ptype: str = "write") -> None:
    if frappe.has_permission("Customer", ptype=ptype):
        return
    if _is_privileged():
        return
    frappe.throw(_("Not permitted"), frappe.PermissionError)


def _ensure_loaner_permission(ptype: str = "read") -> None:
    if frappe.has_permission("Loaner Instrument", ptype=ptype):
        return
    if _is_privileged():
        return
    frappe.throw(_("Not permitted"), frappe.PermissionError)


def _coerce_dict(value: Any) -> dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    try:
        parsed = frappe.parse_json(value)
    except Exception:
        return {}
    return parsed or {}


def _build_print_url(doctype: str, name: str, format_name: str) -> str:
    encoded_doctype = quote(doctype)
    encoded_name = quote(name)
    encoded_format = quote(format_name)
    return f"/printview?doctype={encoded_doctype}&name={encoded_name}&format={encoded_format}"


def _touch_session_event(session: Any, event_type: str, payload: dict[str, Any] | None = None) -> None:
    if not session:
        return
    try:
        session.append_event(event_type, payload or {})
        session.save(ignore_permissions=True)
    except Exception:
        LOGGER.error("Failed to append intake session event", exc_info=True)


def _get_session(session_id: str | None, *, create: bool = False) -> Any:
    if session_id:
        if not frappe.db.exists("Intake Session", session_id):
            frappe.throw(_("Unknown intake session"))
        session_doc = frappe.get_doc("Intake Session", session_id)
        session_doc.check_permission("write")
        return session_doc

    if not create:
        return None

    doc = frappe.get_doc({
        "doctype": "Intake Session",
    })
    doc.insert()
    return doc


def _update_session_payload(session: Any, payload: dict[str, Any], *, last_step: str | None = None, status: str | None = None) -> None:
    if not session:
        return
    if "customer" in payload:
        session.customer_json = payload.get("customer")
    if "instrument" in payload:
        session.instrument_json = payload.get("instrument")
    if "player" in payload:
        session.player_json = payload.get("player")
    if "intake" in payload:
        intake_block = session.intake_json or {}
        if isinstance(intake_block, str):
            intake_block = frappe.parse_json(intake_block) or {}
        intake_block.update(payload.get("intake") or {})
        session.intake_json = intake_block
    if last_step:
        session.last_step = last_step
    if status:
        session.status = status
    session.error_trace = None
    session.save()


def _serialize_session(session: Any) -> dict[str, Any]:
    if not session:
        return {}
    return {
        "name": session.name,
        "session_id": session.session_id,
        "status": session.status,
        "customer_json": _coerce_dict(session.customer_json),
        "instrument_json": _coerce_dict(session.instrument_json),
        "player_json": _coerce_dict(session.player_json),
        "intake_json": _coerce_dict(session.intake_json),
        "last_step": session.last_step,
        "expires_on": session.expires_on,
        "created_by": session.created_by,
        "error_trace": session.error_trace,
    }


def _build_intake_links(intake_doc: Any) -> dict[str, Any]:
    instrument_name = getattr(intake_doc, "instrument", None)
    links = {
        "intake_name": intake_doc.name,
        "intake_form_route": f"/app/clarinet-intake/{intake_doc.name}",
        "intake_receipt_print": _build_print_url("Clarinet Intake", intake_doc.name, "Intake Receipt"),
        "instrument_tag_print": None,
        "instrument_qr_print": None,
        "create_repair_request_route": "/app/repair-request/new-repair-request",
    }
    if instrument_name:
        links["instrument_form_route"] = f"/app/instrument/{instrument_name}"
    if getattr(intake_doc, "serial_no", None):
        links["instrument_tag_print"] = _build_print_url("Instrument", instrument_name or intake_doc.name, "Instrument Tag")
        links["instrument_qr_print"] = _build_print_url("Instrument", instrument_name or intake_doc.name, "Instrument QR Tag")
    return links


def _resolve_player_docname(data: dict[str, Any]) -> str | None:
    if data.get("name") and frappe.db.exists("Player Profile", data["name"]):
        return data["name"]
    if data.get("player_profile_id") and frappe.db.exists("Player Profile", data["player_profile_id"]):
        return data["player_profile_id"]
    if data.get("primary_email"):
        existing = frappe.db.get_value("Player Profile", {"primary_email": data["primary_email"]}, "name")
        if existing:
            return existing
    return None


# ---------------------------------------------------------------------------
# Backwards-compatible endpoints retained for the Vue wizard (v2)
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def get_instrument_by_serial(serial_no: str) -> dict[str, Any] | None:
    """Secure lookup of instrument details by serial with normalization and brand mapping."""

    _ensure_intake_permission("read")
    if not serial_no:
        return None

    serial_field_type = _ensure_serial_field_type()
    isn_doc = find_by_serial(serial_no)
    instrument_doc = None

    if serial_field_type == "Link" and isn_doc and isn_doc.get("name"):
        instrument_name = frappe.db.get_value("Instrument", {"serial_no": isn_doc["name"]}, "name")
        if instrument_name:
            instrument_doc = frappe.get_doc("Instrument", instrument_name)
    if not instrument_doc:
        instrument_name = frappe.db.get_value("Instrument", {"serial_no": serial_no}, "name")
        if instrument_name:
            instrument_doc = frappe.get_doc("Instrument", instrument_name)

    normalized = normalize_serial(serial_no)
    response: dict[str, Any] = {
        "serial_input": serial_no,
        "normalized_serial": normalized,
        "match": bool(instrument_doc),
        "instrument": None,
        "instrument_name": getattr(instrument_doc, "name", None),
        "instrument_serial_number": isn_doc.get("name") if isn_doc else None,
        "brand_mapping": None,
    }

    if instrument_doc:
        data = {
            "name": instrument_doc.name,
            "manufacturer": getattr(instrument_doc, "brand", None),
            "model": getattr(instrument_doc, "model", None),
            "clarinet_type": getattr(instrument_doc, "clarinet_type", None),
            "body_material": getattr(instrument_doc, "body_material", None),
            "key_plating": getattr(instrument_doc, "key_plating", None),
            "instrument_category": getattr(instrument_doc, "instrument_category", None),
        }
        if data.get("manufacturer"):
            response["brand_mapping"] = {
                "input": data["manufacturer"],
                "mapped": map_brand(data["manufacturer"]),
            }
            data["manufacturer"] = response["brand_mapping"]["mapped"]
        response["instrument"] = data

    LOGGER.info(
        "intake.get_instrument_by_serial",
        extra={"serial": serial_no, "normalized": normalized, "matched": response["match"]},
    )
    return response


@frappe.whitelist(allow_guest=False)
def get_instrument_inspection_name(intake_record_id: str) -> str | None:
    """Return the Instrument Inspection name linked to a given intake, if any."""

    _ensure_intake_permission("read")
    if not intake_record_id:
        return None
    return frappe.db.get_value(
        "Instrument Inspection", {"intake_record_id": intake_record_id}, "name"
    )


@frappe.whitelist(allow_guest=False)
def upsert_customer(payload: dict[str, Any]) -> dict[str, Any]:
    """Idempotently create or update a Customer/Contact/Address tuple via intake_sync."""

    _ensure_customer_permission("write")
    data = _coerce_dict(payload)
    LOGGER.info("intake.upsert_customer", extra={"keys": list(data.keys())})
    customer_name = intake_sync.upsert_customer(data)
    return {
        "customer": customer_name,
        "link": get_link_to_form("Customer", customer_name),
    }


@frappe.whitelist(allow_guest=False)
def upsert_player_profile(payload: dict[str, Any]) -> dict[str, Any]:
    """Create or update a Player Profile with idempotent matching on email/profile ID."""

    _ensure_player_permission("write")
    data = _coerce_dict(payload)
    filtered = {k: v for k, v in data.items() if k in _ALLOWED_PLAYER_FIELDS}
    if not filtered.get("player_name") or not filtered.get("primary_email"):
        frappe.throw(_("Player name and primary email are required."))

    existing_name = _resolve_player_docname(filtered)
    if existing_name:
        doc = frappe.get_doc("Player Profile", existing_name)
        doc.update(filtered)
        doc.save()
    else:
        doc = frappe.get_doc({"doctype": "Player Profile", **filtered})
        doc.insert()

    LOGGER.info("intake.upsert_player_profile", extra={"player": doc.name})
    return {
        "player_profile": doc.name,
        "link": get_link_to_form("Player Profile", doc.name),
    }


@frappe.whitelist(allow_guest=False)
def list_available_loaners(filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return available loaner instruments for the wizard."""

    _ensure_loaner_permission("read")
    data = _coerce_dict(filters)
    base_filters: list[Sequence[Any]] = [["status", "in", ["Draft", "Returned"]]]
    if data.get("linked_intake"):
        base_filters.append(["linked_intake", "=", data["linked_intake"]])
    if data.get("loaner"):
        base_filters.append(["name", "=", data["loaner"]])

    loaners = frappe.get_all(
        "Loaner Instrument",
        filters=base_filters,
        fields=[
            "name",
            "instrument",
            "status",
            "issue_date",
            "due_date",
            "returned",
        ],
        order_by="modified desc",
        limit_page_length=25,
    )
    result: list[dict[str, Any]] = []
    for row in loaners:
        instrument_doc = None
        if row.get("instrument"):
            try:
                instrument_doc = frappe.get_doc("Instrument", row["instrument"])
            except Exception:
                instrument_doc = None
        result.append(
            {
                "loaner": row["name"],
                "instrument": row.get("instrument"),
                "status": row.get("status"),
                "due_date": row.get("due_date"),
                "returned": row.get("returned"),
                "instrument_details": {
                    "manufacturer": getattr(instrument_doc, "brand", None) if instrument_doc else None,
                    "model": getattr(instrument_doc, "model", None) if instrument_doc else None,
                    "serial_no": getattr(instrument_doc, "serial_no", None) if instrument_doc else None,
                },
            }
        )
    LOGGER.info("intake.list_available_loaners", extra={"count": len(result)})
    return result


@frappe.whitelist(allow_guest=False)
def save_intake_session(
    payload: dict[str, Any] | None = None,
    session_id: str | None = None,
    last_step: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """Persist wizard progress and telemetry."""

    _ensure_intake_permission("write")
    data = _coerce_dict(payload)
    session = _get_session(session_id, create=True)
    _update_session_payload(session, data, last_step=last_step, status=status)
    _touch_session_event(session, "api_call", {"operation": "save_session", "step": last_step})
    return _serialize_session(session)


@frappe.whitelist(allow_guest=False)
def load_intake_session(session_id: str) -> dict[str, Any]:
    """Return stored wizard payload for the provided session."""

    _ensure_intake_permission("read")
    if not session_id:
        frappe.throw(_("Session ID is required"))
    session = _get_session(session_id, create=False)
    if not session:
        frappe.throw(_("Session not found"))
    session.check_permission("read")
    _touch_session_event(session, "api_call", {"operation": "load_session"})
    return _serialize_session(session)


@frappe.whitelist(allow_guest=False)
def create_intake(payload: dict[str, Any], session_id: str | None = None) -> dict[str, Any]:
    """Transactional creation of Clarinet Intake (and optional loaner agreement)."""

    _ensure_intake_permission("write")
    data = _coerce_dict(payload)
    intake_data = data.get("intake")
    if not intake_data:
        frappe.throw(_("Intake data is required."))

    session = _get_session(session_id, create=False)
    if session:
        session.check_permission("write")

    LOGGER.info("intake.create_intake.start", extra={"session": session_id, "keys": list(data.keys())})

    frappe.db.savepoint("intake_wizard")
    try:
        intake_doc = frappe.get_doc({"doctype": "Clarinet Intake", **intake_data})
        intake_doc.insert()

        loaner_response: dict[str, Any] | None = None
        if data.get("loaner_agreement"):
            loaner_payload = _coerce_dict(data.get("loaner_agreement"))
            if loaner_payload.get("linked_intake") is None:
                loaner_payload["linked_intake"] = intake_doc.name
            loaner_doc = frappe.get_doc({"doctype": "Loaner Agreement", **loaner_payload})
            loaner_doc.insert()
            if not loaner_doc.linked_intake:
                loaner_doc.linked_intake = intake_doc.name
            loaner_doc.submit()
            loaner_response = {"loaner_agreement": loaner_doc.name}

        links = _build_intake_links(intake_doc)
        if loaner_response:
            links.update(loaner_response)

        if session:
            session.status = "Submitted"
            session.error_trace = None
            _touch_session_event(session, "submit_success", {"intake": intake_doc.name})

        LOGGER.info("intake.create_intake.success", extra={"intake": intake_doc.name})
        return links
    except Exception:
        frappe.db.rollback("intake_wizard")
        LOGGER.error("intake.create_intake.error", exc_info=True)
        if session:
            session.status = "Abandoned"
            session.error_trace = frappe.get_traceback()
            _touch_session_event(session, "submit_error", {"error": session.error_trace})
        frappe.throw(_("Failed to create intake."))


# Legacy compatibility helper retained
@frappe.whitelist(allow_guest=False)
def get_intake_session(session_id: str) -> dict[str, Any]:
    """Compatibility wrapper for load_intake_session."""

    return load_intake_session(session_id)
