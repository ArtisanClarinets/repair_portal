
# Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/api.py
# Last Updated: 2025-10-11
# Version: v3.0.0 (Fortune-500 intake API surface)
# Purpose:
#   Hardened API surface for the Intake wizard and supporting flows.
#   • Implements audited, rate-limited endpoints powering the intake wizard.
#   • Enforces least-privilege role checks, idempotency, and structured telemetry.
#   • Reuses existing intake services for customer sync, serial handling, and settings.

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Iterable

import frappe
from frappe import _
from frappe.utils import add_to_date, now_datetime
from frappe.model.document import Document

from repair_portal.intake.doctype.brand_mapping_rule.brand_mapping_rule import map_brand
from repair_portal.intake.services import intake_sync
from repair_portal.repair_portal.doctype.clarinet_intake_settings.clarinet_intake_settings import (
    get_intake_settings,
)
from repair_portal.intake.doctype.intake_session.intake_session import IntakeSession
from repair_portal.utils.serials import ensure_instrument_serial, find_by_serial, normalize_serial


_REQUIRED_ROLES = {"System Manager", "Repair Manager", "Intake Coordinator"}
_IDEMP_CACHE_PREFIX = "intake_api:idempotency"
_DEFAULT_SLA_HOURS = 72
_DEFAULT_SLA_LABEL = "Promise by"
_SEARCH_CUSTOMER_FIELDS = ["name", "customer_name", "email_id", "mobile_no"]
_SEARCH_INSTRUMENT_FIELDS = ["name", "serial_no", "brand", "model", "customer"]
_PLAYER_FIELDS = {
    "player_name",
    "preferred_name",
    "primary_email",
    "primary_phone",
    "player_level",
    "customer",
    "newsletter_subscription",
    "targeted_marketing_optin",
    "mailing_address",
}


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


def _get_request_ip() -> str:
    return getattr(frappe.local, "request_ip", None) or "0.0.0.0"


def _request_hash(payload: Any) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":")) if isinstance(payload, dict) else frappe.as_unicode(payload)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"sha256-{digest}"


def _mask_email(value: str | None) -> str | None:
    if not value or "@" not in value:
        return value
    local, domain = value.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}"
    return f"{masked_local}@{domain}"


def _mask_phone(value: str | None) -> str | None:
    if not value:
        return value
    digits = [ch for ch in value if ch.isdigit()]
    if len(digits) <= 4:
        return "***"
    return f"***-***-{''.join(digits[-4:])}"


def _mask_value(value: Any) -> Any:
    if isinstance(value, str):
        if "@" in value:
            return _mask_email(value)
        if any(ch.isdigit() for ch in value):
            return _mask_phone(value)
    return value


def _safe_refs(refs: dict[str, Any]) -> dict[str, Any]:
    return {key: _mask_value(val) if key in {"email", "phone"} else val for key, val in refs.items()}


def _require_roles(required: Iterable[str]) -> None:
    user = frappe.session.user
    if user == "Administrator":
        return
    roles = set(frappe.get_roles(user))
    if not roles.intersection(set(required)):
        raise frappe.PermissionError(_("You are not permitted to perform this intake operation."))


def _rate_limit(key: str, limit: int, window_seconds: int) -> None:
    cache = frappe.cache()
    user = frappe.session.user or "Guest"
    cache_key = f"intake_api:{user}:{key}"
    current = cache.incr(cache_key)
    if current == 1:
        cache.expire(cache_key, window_seconds)
    if current > limit:
        cache.expire(cache_key, window_seconds)
        raise frappe.TooManyRequestsError(_("You are performing this action too frequently. Please wait a moment."))


def _idempotency_key(payload: dict | str | None, session_id: str | None) -> str:
    if session_id:
        source = session_id
    else:
        if isinstance(payload, dict):
            normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        else:
            normalized = frappe.as_unicode(payload or "")
        bucket = now_datetime().replace(minute=0, second=0, microsecond=0).isoformat()
        source = f"{normalized}|{bucket}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _get_idempotent_result(idempotency_key: str) -> dict[str, Any] | None:
    cache = frappe.cache()
    cached = cache.get_value(f"{_IDEMP_CACHE_PREFIX}:{idempotency_key}")
    if not cached:
        return None
    try:
        return frappe.parse_json(cached) or None
    except Exception:
        return None


def _remember_idempotent_result(idempotency_key: str, result: dict[str, Any]) -> None:
    cache = frappe.cache()
    cache.set_value(f"{_IDEMP_CACHE_PREFIX}:{idempotency_key}", json.dumps(result), expires_in_sec=300)


def _log(channel: str, event: dict[str, Any]) -> None:
    baseline = {
        "op": event.get("op"),
        "status": event.get("status"),
        "actor": frappe.session.user,
        "ip": event.get("ip") or _get_request_ip(),
        "session_id": event.get("session_id"),
        "idempotency_key": event.get("idempotency_key"),
        "request_hash": event.get("request_hash"),
        "timings_ms": event.get("timings_ms", {"total": 0, "db": 0}),
        "refs": _safe_refs(event.get("refs", {})),
    }
    if event.get("err"):
        baseline["err"] = event["err"]
    frappe.logger(channel).info(baseline)


def _get_session(session_id: str | None, *, for_write: bool = False) -> IntakeSession | None:
    if not session_id:
        return None
    if not frappe.db.exists("Intake Session", session_id):
        frappe.throw(_("Unknown intake session."), frappe.DoesNotExistError)
    session = frappe.get_doc("Intake Session", session_id)
    session.check_permission("write" if for_write else "read")
    return session


def _append_session_event(session: IntakeSession | None, event_type: str, payload: dict[str, Any] | None = None) -> None:
    if not session:
        return
    try:
        session.append_event(event_type, payload or {})
        session.save(ignore_permissions=True)
    except Exception:
        frappe.logger("intake_ui_audit").error(
            "Failed to append intake session telemetry", exc_info=True
        )


def _fetch_contact_name(email: str | None, phone: str | None) -> str | None:
    if email:
        contact = frappe.db.get_value("Contact", {"email_id": email}, "name")
        if contact:
            return contact
    if phone:
        contact = frappe.db.get_value("Contact Phone", {"phone": phone}, "parent")
        if contact:
            return contact
    return None


def _fetch_address_name(customer: str) -> str | None:
    return frappe.db.get_value(
        "Dynamic Link",
        {
            "link_doctype": "Customer",
            "link_name": customer,
            "parenttype": "Address",
        },
        "parent",
    )


def _resolve_customer(payload: dict[str, Any]) -> dict[str, Any]:
    customer_name = intake_sync.upsert_customer(payload)
    email = payload.get("email") or payload.get("email_id")
    phone = payload.get("phone") or payload.get("mobile_no")
    contact_name = _fetch_contact_name(email, phone)
    address_name = _fetch_address_name(customer_name)
    return {"customer": customer_name, "contact": contact_name, "address": address_name}


def _resolve_player_profile(payload: dict[str, Any]) -> str:
    data = {k: v for k, v in payload.items() if k in _PLAYER_FIELDS}
    if not data.get("player_name") or not data.get("primary_email"):
        frappe.throw(_("Player name and primary email are required."))
    player_name = None
    if payload.get("player_profile") and frappe.db.exists("Player Profile", payload["player_profile"]):
        player_name = payload["player_profile"]
    if not player_name:
        player_name = frappe.db.get_value("Player Profile", {"primary_email": data["primary_email"]}, "name")
    if not player_name and data.get("primary_phone"):
        player_name = frappe.db.get_value("Player Profile", {"primary_phone": data["primary_phone"]}, "name")
    default_level = "Amateur/Hobbyist"
    if player_name:
        doc = frappe.get_doc("Player Profile", player_name)
        doc.update(data)
        if not doc.player_level:
            doc.player_level = default_level
        doc.save()
        return doc.name
    doc = frappe.get_doc(
        {
            "doctype": "Player Profile",
            **data,
            "player_level": data.get("player_level") or default_level,
        }
    )
    doc.insert()
    return doc.name


def _brand_from_payload(payload: dict[str, Any]) -> str | None:
    brand = payload.get("brand") or payload.get("manufacturer")
    if not brand:
        return None
    mapped = map_brand(brand)
    payload["brand"] = mapped
    payload.setdefault("manufacturer", mapped)
    return mapped


def _default_instrument_category() -> str | None:
    return frappe.db.get_value("Instrument Category", {"is_active": 1}, "name")


def _find_existing_instrument(serial: str | None, named: str | None) -> tuple[str | None, dict[str, Any] | None]:
    if named and frappe.db.exists("Instrument", named):
        doc = frappe.get_doc("Instrument", named)
        return doc.name, doc.as_dict()
    if not serial:
        return None, None
    isn = find_by_serial(serial)
    if isn and isn.get("instrument") and frappe.db.exists("Instrument", isn["instrument"]):
        doc = frappe.get_doc("Instrument", isn["instrument"])
        return doc.name, doc.as_dict()
    instrument_name = frappe.db.get_value("Instrument", {"serial_no": serial}, "name")
    if instrument_name:
        doc = frappe.get_doc("Instrument", instrument_name)
        return doc.name, doc.as_dict()
    return None, None


def _find_or_create_instrument(payload: dict[str, Any], customer: str | None) -> tuple[str, str]:
    serial_input = payload.get("serial_no") or payload.get("serial")
    normalized_serial = normalize_serial(serial_input)
    if not normalized_serial:
        frappe.throw(_("A valid serial number is required."))
    existing_name, existing_doc = _find_existing_instrument(normalized_serial, payload.get("name"))
    brand = _brand_from_payload(payload)
    if existing_name:
        if brand and existing_doc and existing_doc.get("brand") != brand:
            frappe.db.set_value("Instrument", existing_name, "brand", brand)
        return existing_name, normalized_serial
    clarinet_type = payload.get("clarinet_type") or payload.get("instrument_type") or "B♭ Clarinet"
    instrument = frappe.get_doc(
        {
            "doctype": "Instrument",
            "serial_no": normalized_serial,
            "instrument_type": clarinet_type,
            "clarinet_type": clarinet_type,
            "brand": brand,
            "model": payload.get("model"),
            "customer": customer,
            "instrument_category": payload.get("instrument_category") or _default_instrument_category(),
            "current_status": payload.get("current_status") or "Active",
        }
    )
    instrument.insert()
    ensure_instrument_serial(serial_input=serial_input or normalized_serial, instrument=instrument.name)
    return instrument.name, normalized_serial


def resolve_sla(intake_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = get_intake_settings()
    hours = settings.get("sla_target_hours") or _DEFAULT_SLA_HOURS
    try:
        hours = int(hours)
    except (TypeError, ValueError):
        hours = _DEFAULT_SLA_HOURS
    label = settings.get("sla_label") or _DEFAULT_SLA_LABEL
    target_dt = add_to_date(now_datetime(), hours=hours)
    return {"target_dt": target_dt, "label": label}


@frappe.whitelist(allow_guest=False)
def search_customers(query: str) -> list[dict[str, Any]]:
    start = time.perf_counter()
    payload = {"query": query}
    request_hash = _request_hash(payload)
    _require_roles(_REQUIRED_ROLES)
    _rate_limit("search_customers", 120, 60)
    or_filters = []
    if query:
        like_query = f"%{query}%"
        or_filters = [
            ["customer_name", "like", like_query],
            ["email_id", "like", like_query],
            ["mobile_no", "like", like_query],
        ]
    customers = frappe.db.get_list(
        "Customer",
        fields=_SEARCH_CUSTOMER_FIELDS,
        or_filters=or_filters,
        limit=20,
        order_by="modified desc",
    )
    timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
    _log(
        "intake_ui_audit",
        {
            "op": "search_customers",
            "status": "ok",
            "request_hash": request_hash,
            "timings_ms": timings,
            "refs": {"matches": len(customers)},
        },
    )
    return customers


@frappe.whitelist(allow_guest=False)
def search_instruments(q: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    start = time.perf_counter()
    payload = _coerce_dict(q)
    request_hash = _request_hash(payload)
    _require_roles(_REQUIRED_ROLES)
    _rate_limit("search_instruments", 120, 60)
    filters: list[list[Any]] = []
    serial = payload.get("serial") or payload.get("serial_no")
    normalized = normalize_serial(serial) if serial else None
    if normalized:
        filters.append(["serial_no", "=", normalized])
    if payload.get("brand"):
        filters.append(["brand", "like", f"%{payload['brand']}%"])
    if payload.get("model"):
        filters.append(["model", "like", f"%{payload['model']}%"])
    instruments = frappe.db.get_list(
        "Instrument",
        fields=_SEARCH_INSTRUMENT_FIELDS,
        filters=filters,
        limit=20,
        order_by="modified desc",
    )
    timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
    _log(
        "intake_ui_audit",
        {
            "op": "search_instruments",
            "status": "ok",
            "request_hash": request_hash,
            "timings_ms": timings,
            "refs": {"matches": len(instruments)},
        },
    )
    return instruments


@frappe.whitelist(allow_guest=False)
def upsert_customer(payload: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    data = _coerce_dict(payload)
    request_hash = _request_hash(data)
    _require_roles(_REQUIRED_ROLES)
    _rate_limit("upsert_customer", 60, 60)
    try:
        result = _resolve_customer(data)
    except Exception as exc:
        timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
        _log(
            "intake_ui_security" if isinstance(exc, frappe.PermissionError) else "intake_ui_audit",
            {
                "op": "upsert_customer",
                "status": "error",
                "request_hash": request_hash,
                "timings_ms": timings,
                "err": {"code": exc.__class__.__name__, "msg": frappe.as_unicode(exc)},
            },
        )
        raise
    timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
    _log(
        "intake_ui_audit",
        {
            "op": "upsert_customer",
            "status": "ok",
            "request_hash": request_hash,
            "timings_ms": timings,
            "refs": {"customer": result.get("customer")},
        },
    )
    return result


@frappe.whitelist(allow_guest=False)
def upsert_player_profile(payload: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    data = _coerce_dict(payload)
    request_hash = _request_hash(data)
    _require_roles(_REQUIRED_ROLES)
    _rate_limit("upsert_player_profile", 60, 60)
    try:
        profile_name = _resolve_player_profile(data)
    except Exception as exc:
        timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
        _log(
            "intake_ui_security" if isinstance(exc, frappe.PermissionError) else "intake_ui_audit",
            {
                "op": "upsert_player_profile",
                "status": "error",
                "request_hash": request_hash,
                "timings_ms": timings,
                "err": {"code": exc.__class__.__name__, "msg": frappe.as_unicode(exc)},
            },
        )
        raise
    timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
    _log(
        "intake_ui_audit",
        {
            "op": "upsert_player_profile",
            "status": "ok",
            "request_hash": request_hash,
            "timings_ms": timings,
            "refs": {"player_profile": profile_name},
        },
    )
    return {"player_profile": profile_name}


def _apply_accessories(intake_doc: Document, accessories: list[dict[str, Any]]) -> None:
    if not accessories:
        return
    intake_doc.set("accessory_id", [])
    for row in accessories:
        if not row:
            continue
        intake_doc.append(
            "accessory_id",
            {
                "item_code": row.get("item_code"),
                "description": row.get("description"),
                "qty": row.get("qty") or 1,
                "uom": row.get("uom"),
                "rate": row.get("rate"),
                "amount": row.get("amount"),
            },
        )


def _apply_service_fields(intake_doc: Document, service_payload: dict[str, Any]) -> None:
    if not service_payload:
        return
    mapping = {
        "customers_stated_issue": service_payload.get("issue"),
        "initial_assessment_notes": service_payload.get("notes"),
        "service_type_requested": service_payload.get("service_type"),
        "deposit_paid": service_payload.get("deposit"),
    }
    for fieldname, value in mapping.items():
        if value is not None:
            setattr(intake_doc, fieldname, value)


def _build_intake_refs(intake_doc: Document) -> dict[str, Any]:
    refs = {"intake": intake_doc.name, "instrument": intake_doc.instrument}
    inspection_name = frappe.db.get_value(
        "Instrument Inspection", {"intake_record_id": intake_doc.name}, "name"
    )
    if inspection_name:
        refs["inspection"] = inspection_name
    if getattr(intake_doc, "player_profile", None):
        refs["profile"] = intake_doc.player_profile
    return refs


@frappe.whitelist(allow_guest=False)
def create_full_intake(payload: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    data = _coerce_dict(payload)
    request_hash = _request_hash(data)
    session_id = data.get("session_id")
    idempotency_key = _idempotency_key(data, session_id)
    cached = _get_idempotent_result(idempotency_key)
    if cached:
        timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
        _log(
            "intake_ui_audit",
            {
                "op": "create_full_intake",
                "status": "ok",
                "request_hash": request_hash,
                "idempotency_key": idempotency_key,
                "timings_ms": timings,
                "refs": cached,
            },
        )
        return cached

    _require_roles(_REQUIRED_ROLES)
    _rate_limit("create_full_intake", 30, 60)
    session = None
    try:
        session = _get_session(session_id, for_write=True)
    except Exception:
        session = None

    customer_payload = _coerce_dict(data.get("customer"))
    instrument_payload = _coerce_dict(data.get("instrument"))
    player_payload = _coerce_dict(data.get("player"))
    service_payload = _coerce_dict(data.get("service"))
    intake_payload = _coerce_dict(data.get("intake"))

    frappe.db.savepoint("create_full_intake")
    try:
        customer_result = _resolve_customer(customer_payload)
        player_profile = None
        if player_payload:
            player_profile = _resolve_player_profile(player_payload)

        instrument_name, normalized_serial = _find_or_create_instrument(
            instrument_payload, customer_result.get("customer")
        )

        intake_doc = frappe.get_doc({"doctype": "Clarinet Intake", **intake_payload})
        intake_doc.customer = customer_result.get("customer")
        intake_doc.customer_full_name = customer_payload.get("customer_name")
        intake_doc.customer_email = customer_payload.get("email") or customer_payload.get("email_id")
        intake_doc.customer_phone = customer_payload.get("phone") or customer_payload.get("mobile_no")
        intake_doc.instrument = instrument_name
        intake_doc.serial_no = normalized_serial
        intake_doc.instrument_category = (
            intake_payload.get("instrument_category")
            or instrument_payload.get("instrument_category")
            or _default_instrument_category()
        )
        intake_doc.manufacturer = instrument_payload.get("brand") or instrument_payload.get("manufacturer")
        intake_doc.model = instrument_payload.get("model")
        intake_doc.clarinet_type = (
            intake_payload.get("clarinet_type")
            or instrument_payload.get("clarinet_type")
            or "B♭ Clarinet"
        )
        if player_profile:
            intake_doc.player_profile = player_profile
        _apply_service_fields(intake_doc, service_payload)
        _apply_accessories(intake_doc, service_payload.get("accessories") if service_payload else [])

        sla_info = resolve_sla(intake_payload)
        if sla_info.get("target_dt"):
            intake_doc.promised_completion_date = sla_info["target_dt"].date()

        intake_doc.insert()
        intake_doc.submit()

        refs = _build_intake_refs(intake_doc)

        loaner_payload = _coerce_dict(data.get("loaner"))
        loaner_name = None
        if loaner_payload:
            loaner_name = loaner_payload.get("loaner") or loaner_payload.get("name")
        if loaner_name:
            current_status = frappe.db.get_value("Loaner Instrument", loaner_name, "status")
            if current_status not in {"Draft", "Returned", "Available"}:
                frappe.throw(_("Selected loaner instrument is not available."))
            frappe.db.set_value("Loaner Instrument", loaner_name, "intake", intake_doc.name)
            refs["loaner"] = loaner_name

        _remember_idempotent_result(idempotency_key, refs)

        if session:
            session.status = "Submitted"
            session.error_trace = None
            session.save(ignore_permissions=True)
            _append_session_event(session, "submit_success", {"intake": intake_doc.name})

        timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
        _log(
            "intake_ui_audit",
            {
                "op": "create_full_intake",
                "status": "ok",
                "request_hash": request_hash,
                "idempotency_key": idempotency_key,
                "session_id": session_id,
                "timings_ms": timings,
                "refs": refs,
            },
        )
        return refs
    except Exception as exc:
        frappe.db.rollback("create_full_intake")
        if session:
            session.status = "Abandoned"
            session.error_trace = frappe.get_traceback()
            session.save(ignore_permissions=True)
            _append_session_event(session, "submit_error", {"error": frappe.as_unicode(exc)})
        timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
        _log(
            "intake_ui_security" if isinstance(exc, frappe.PermissionError) else "intake_ui_audit",
            {
                "op": "create_full_intake",
                "status": "error",
                "request_hash": request_hash,
                "idempotency_key": idempotency_key,
                "session_id": session_id,
                "timings_ms": timings,
                "err": {"code": exc.__class__.__name__, "msg": frappe.as_unicode(exc)},
            },
        )
        raise


@frappe.whitelist(allow_guest=False)
def loaner_prepare(payload: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    data = _coerce_dict(payload)
    request_hash = _request_hash(data)
    _require_roles(_REQUIRED_ROLES)
    _rate_limit("loaner_prepare", 30, 60)
    loaner_name = data.get("loaner") or data.get("name")
    if not loaner_name:
        frappe.throw(_("Loaner identifier is required."))
    if not frappe.db.exists("Loaner Instrument", loaner_name):
        frappe.throw(_("Loaner Instrument not found."))
    status = frappe.db.get_value("Loaner Instrument", loaner_name, "status")
    if status not in {"Draft", "Returned", "Available"}:
        timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
        _log(
            "intake_ui_security",
            {
                "op": "loaner_prepare",
                "status": "error",
                "request_hash": request_hash,
                "refs": {"loaner": loaner_name, "status": status},
                "timings_ms": timings,
                "err": {"code": "LoanerUnavailable", "msg": _("Loaner is not currently available.")},
            },
        )
        frappe.throw(_("Selected loaner instrument is not available."))
    timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
    _log(
        "intake_ui_audit",
        {
            "op": "loaner_prepare",
            "status": "ok",
            "request_hash": request_hash,
            "refs": {"loaner": loaner_name, "status": status},
            "timings_ms": timings,
        },
    )
    return {"loaner": loaner_name}


# ---------------------------------------------------------------------------
# Backwards-compatible endpoints retained for the Vue wizard (v2)
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def get_instrument_by_serial(serial_no: str) -> dict[str, Any] | None:
    start = time.perf_counter()
    payload = {"serial_no": serial_no}
    request_hash = _request_hash(payload)
    _require_roles(_REQUIRED_ROLES)
    _rate_limit("get_instrument_by_serial", 120, 60)

    if not serial_no:
        timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
        _log(
            "intake_ui_audit",
            {
                "op": "get_instrument_by_serial",
                "status": "ok",
                "request_hash": request_hash,
                "timings_ms": timings,
                "refs": {"match": False},
            },
        )
        return None

    normalized = normalize_serial(serial_no)
    isn_doc = find_by_serial(serial_no)
    instrument = None
    if isn_doc and isn_doc.get("instrument") and frappe.db.exists("Instrument", isn_doc["instrument"]):
        instrument = frappe.get_doc("Instrument", isn_doc["instrument"])
    elif normalized and frappe.db.exists("Instrument", {"serial_no": normalized}):
        instrument_name = frappe.db.get_value("Instrument", {"serial_no": normalized}, "name")
        instrument = frappe.get_doc("Instrument", instrument_name)
    response = {
        "serial_input": serial_no,
        "normalized_serial": normalized,
        "match": bool(instrument),
        "instrument_name": instrument.name if instrument else None,
        "instrument": instrument.as_dict() if instrument else None,
        "instrument_serial_number": isn_doc.get("name") if isn_doc else None,
    }
    timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
    _log(
        "intake_ui_audit",
        {
            "op": "get_instrument_by_serial",
            "status": "ok",
            "request_hash": request_hash,
            "timings_ms": timings,
            "refs": {"match": response["match"], "instrument": response.get("instrument_name")},
        },
    )
    return response


@frappe.whitelist(allow_guest=False)
def list_available_loaners(filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    start = time.perf_counter()
    data = _coerce_dict(filters)
    request_hash = _request_hash(data)
    _require_roles(_REQUIRED_ROLES)
    _rate_limit("list_available_loaners", 60, 60)

    base_filters = [["status", "in", ["Draft", "Returned", "Available"]]]
    if data.get("linked_intake"):
        base_filters.append(["linked_intake", "=", data["linked_intake"]])
    loaners = frappe.get_all(
        "Loaner Instrument",
        filters=base_filters,
        fields=["name", "instrument", "status", "issue_date", "due_date", "returned"],
        order_by="modified desc",
        limit_page_length=25,
    )
    result = [
        {
            "loaner": row["name"],
            "instrument": row.get("instrument"),
            "status": row.get("status"),
            "due_date": row.get("due_date"),
            "returned": row.get("returned"),
        }
        for row in loaners
    ]
    timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
    _log(
        "intake_ui_audit",
        {
            "op": "list_available_loaners",
            "status": "ok",
            "request_hash": request_hash,
            "timings_ms": timings,
            "refs": {"matches": len(result)},
        },
    )
    return result


@frappe.whitelist(allow_guest=False)
def save_intake_session(
    payload: dict[str, Any] | None = None,
    session_id: str | None = None,
    last_step: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()
    _require_roles(_REQUIRED_ROLES)
    _rate_limit("save_intake_session", 90, 60)
    data = _coerce_dict(payload)
    request_hash = _request_hash({"payload": data, "session_id": session_id, "last_step": last_step, "status": status})

    session = _get_session(session_id, for_write=True)
    if not session:
        session = frappe.get_doc({"doctype": "Intake Session"})
        session.insert()
    if "customer" in data:
        session.customer_json = data.get("customer")
    if "instrument" in data:
        session.instrument_json = data.get("instrument")
    if "player" in data:
        session.player_json = data.get("player")
    if "intake" in data:
        session.intake_json = data.get("intake")
    if last_step:
        session.last_step = last_step
    if status:
        session.status = status
    session.error_trace = None
    session.save()
    _append_session_event(session, "api_call", {"operation": "save_session", "step": last_step})
    timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
    _log(
        "intake_ui_audit",
        {
            "op": "save_intake_session",
            "status": "ok",
            "request_hash": request_hash,
            "session_id": session.session_id,
            "timings_ms": timings,
            "refs": {"status": session.status, "last_step": session.last_step},
        },
    )
    return {
        "name": session.name,
        "session_id": session.session_id,
        "status": session.status,
        "customer_json": session.customer_json,
        "instrument_json": session.instrument_json,
        "player_json": session.player_json,
        "intake_json": session.intake_json,
        "last_step": session.last_step,
        "expires_on": session.expires_on,
        "created_by": session.created_by,
        "error_trace": session.error_trace,
    }


@frappe.whitelist(allow_guest=False)
def load_intake_session(session_id: str) -> dict[str, Any]:
    start = time.perf_counter()
    _require_roles(_REQUIRED_ROLES)
    _rate_limit("load_intake_session", 120, 60)
    request_hash = _request_hash({"session_id": session_id})
    session = _get_session(session_id, for_write=False)
    if not session:
        frappe.throw(_("Session not found"))
    _append_session_event(session, "api_call", {"operation": "load_session"})
    timings = {"total": int((time.perf_counter() - start) * 1000), "db": 0}
    _log(
        "intake_ui_audit",
        {
            "op": "load_intake_session",
            "status": "ok",
            "request_hash": request_hash,
            "session_id": session.session_id,
            "timings_ms": timings,
            "refs": {"status": session.status, "last_step": session.last_step},
        },
    )
    return {
        "name": session.name,
        "session_id": session.session_id,
        "status": session.status,
        "customer_json": session.customer_json,
        "instrument_json": session.instrument_json,
        "player_json": session.player_json,
        "intake_json": session.intake_json,
        "last_step": session.last_step,
        "expires_on": session.expires_on,
        "created_by": session.created_by,
        "error_trace": session.error_trace,
    }


@frappe.whitelist(allow_guest=False)
def create_intake(payload: dict[str, Any], session_id: str | None = None) -> dict[str, Any]:
    _require_roles(_REQUIRED_ROLES)
    data = _coerce_dict(payload)
    data["session_id"] = session_id
    return create_full_intake(data)


@frappe.whitelist(allow_guest=False)
def get_intake_session(session_id: str) -> dict[str, Any]:
    _require_roles(_REQUIRED_ROLES)
    return load_intake_session(session_id)
