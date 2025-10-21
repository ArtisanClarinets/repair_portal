# Path: repair_portal/repair_portal/utils/serials.py
# Purpose: Server-side helpers for Instrument Serial Number lifecycle
# Notes:
# - Idempotent creation/linking of Instrument Serial Number (ISN)
# - Works whether Instrument.serial_no is a Link (to ISN) or Data (raw/legacy)
# - Tries to import normalize_serial from the ISN controller (single source of truth),
#   with robust fallbacks so this module never breaks if import order changes.

from __future__ import annotations

from typing import Any

import frappe
from frappe import _

# -------- Normalization (single source of truth if available) --------
try:
    from repair_portal.instrument_profile.doctype.instrument_serial_number.instrument_serial_number import (
        normalize_serial as _controller_normalize_serial,  # type: ignore
    )

    _HAVE_CONTROLLER_NORMALIZE = True
except Exception:
    _HAVE_CONTROLLER_NORMALIZE = False

if not _HAVE_CONTROLLER_NORMALIZE:
    import re

    _ALNUM_UPPER = re.compile(r"[^A-Z0-9]")

    def _controller_normalize_serial(s: str | None) -> str | None:
        if not s:
            return None
        s = s.strip().upper()
        s = _ALNUM_UPPER.sub("", s)
        return s or None


# --------------------------
# Public API
# --------------------------


def normalize_serial(s: str | None) -> str | None:
    """Public re-export for consistency."""
    return _controller_normalize_serial(s)


def ensure_instrument_serial(
    *,
    serial_input: str,
    instrument: str | None = None,
    scan_code: str | None = None,
    status: str = "Active",
    serial_source: str | None = None,
    verification_status: str | None = None,
    link_on_instrument: bool = True,
    update_if_exists: bool = True,
) -> str:
    """
    Idempotently ensure an Instrument Serial Number exists (and is linked).
    Returns the ISN name.

    Behavior:
      1) Normalize serial.
      2) If matching ISN exists:
           - Optionally link to `instrument` if ISN.instrument is empty.
           - Optionally set scan_code/serial_source/status/verification_status if missing.
           - Optionally set Instrument.serial_no to this ISN (when Link field exists).
      3) Otherwise create ISN; then optionally link to Instrument and set Instrument.serial_no.
    """
    if not serial_input:
        raise frappe.ValidationError(_("Serial input is required"))

    norm = normalize_serial(serial_input)
    if not norm:
        raise frappe.ValidationError(_("Could not derive a normalized serial from input"))

    # Prefer an existing record with this normalized serial
    isn_name = frappe.db.get_value(
        "Instrument Serial Number",
        {"normalized_serial": norm},
        "name",
    )

    if isn_name:
        if update_if_exists:
            _update_existing_isn(
                isn_name,  # type: ignore
                instrument=instrument,
                scan_code=scan_code,
                status=status,
                serial_source=serial_source,
                verification_status=verification_status,
            )
            if link_on_instrument and instrument:
                _try_link_isn_on_instrument(instrument, isn_name)  # type: ignore
        return isn_name  # type: ignore

    # Create new ISN
    doc = frappe.get_doc(
        {
            "doctype": "Instrument Serial Number",
            "serial": serial_input.strip(),
            "instrument": instrument,
            "scan_code": scan_code,
            "status": status,
            "serial_source": serial_source,
            "verification_status": verification_status,
        }
    )
    doc.insert(ignore_permissions=True)
    isn_name = doc.name

    if link_on_instrument and instrument:
        _try_link_isn_on_instrument(instrument, isn_name)  # type: ignore

    return isn_name  # type: ignore


def attach_to_instrument(*, isn_name: str, instrument: str, link_on_instrument: bool = True) -> str:
    """
    Set ISN.instrument = instrument and optionally update Instrument.serial_no (when Link).
    """
    if not frappe.db.exists("Instrument Serial Number", isn_name):
        raise frappe.DoesNotExistError(isn_name)
    if not frappe.db.exists("Instrument", instrument):
        raise frappe.DoesNotExistError(instrument)

    frappe.db.set_value("Instrument Serial Number", isn_name, "instrument", instrument)

    if link_on_instrument:
        _try_link_isn_on_instrument(instrument, isn_name)

    return isn_name


def find_by_serial(serial_input: str) -> dict[str, Any] | None:
    """
    Fetch an ISN by user-entered serial (case/punctuation-insensitive).
    Returns the doc as dict or None.
    """
    if not serial_input:
        return None
    norm = normalize_serial(serial_input)
    if not norm:
        return None
    name = frappe.db.get_value("Instrument Serial Number", {"normalized_serial": norm}, "name")
    if not name:
        return None
    return frappe.db.get_value("Instrument Serial Number", name, "*", as_dict=True)  # type: ignore


def find_by_scan_code(scan_code: str) -> dict[str, Any] | None:
    """Fetch an ISN by shop-applied barcode/QR (exact match)."""
    if not scan_code:
        return None
    name = frappe.db.get_value("Instrument Serial Number", {"scan_code": scan_code}, "name")
    if not name:
        return None
    return frappe.db.get_value("Instrument Serial Number", name, "*", as_dict=True)  # type: ignore


def ensure_from_document(
    *,
    doc: Any,
    serial_field: str = "serial_no",
    instrument_field: str = "instrument",
    scan_code_field: str | None = None,
    status: str = "Active",
    serial_source: str | None = None,
    verification_status: str | None = None,
    link_on_instrument: bool = True,
) -> str | None:
    """Convenience wrapper for calling from other doctypes' hooks (e.g., after_insert)."""
    serial_input = getattr(doc, serial_field, None)
    if not serial_input:
        return None

    instrument = getattr(doc, instrument_field, None)
    scan_code = getattr(doc, scan_code_field, None) if scan_code_field else None

    isn = ensure_instrument_serial(
        serial_input=serial_input,
        instrument=instrument,
        scan_code=scan_code,
        status=status,
        serial_source=serial_source,
        verification_status=verification_status,
        link_on_instrument=link_on_instrument,
    )
    return isn


def candidates(serial_input: str, limit: int = 20) -> list[dict[str, Any]]:
    """
    Return possible matches for a typed serial (normalized).
    """
    if not serial_input:
        return []
    norm = normalize_serial(serial_input)
    if not norm:
        return []
    rows = frappe.get_all(
        "Instrument Serial Number",
        filters={"normalized_serial": norm},
        fields=["name", "instrument", "verification_status", "status"],
        limit=limit,
    )
    return rows


def merge_serials(
    *,
    primary: str,
    duplicate: str,
    mark_duplicate_of: bool = True,
    relink_instrument_field: str = "serial_no",
) -> str:
    """
    Merge `duplicate` into `primary`:
      - Optionally set duplicate.duplicate_of = primary
      - If any Instrument points to `duplicate` via Instrument.serial_no, relink it to `primary`
      - Archive the duplicate by setting status='Deprecated'
    Returns the primary name.
    """
    if primary == duplicate:
        return primary

    if not frappe.db.exists("Instrument Serial Number", primary):
        raise frappe.DoesNotExistError(primary)
    if not frappe.db.exists("Instrument Serial Number", duplicate):
        raise frappe.DoesNotExistError(duplicate)

    if mark_duplicate_of:
        dup = frappe.get_doc("Instrument Serial Number", duplicate)
        dup.duplicate_of = primary  # type: ignore
        if getattr(dup, "status", None) and dup.status != "Deprecated":  # type: ignore
            dup.status = "Deprecated"  # type: ignore
        dup.save(ignore_permissions=True)

    if _instrument_has_field(relink_instrument_field):
        inst_names = frappe.get_all(
            "Instrument",
            filters={relink_instrument_field: duplicate},
            pluck="name",
        )
        for inst_name in inst_names or []:
            frappe.db.set_value("Instrument", inst_name, relink_instrument_field, primary)

    return primary


def backfill_normalized_serial(batch_size: int = 500) -> int:
    """
    One-time utility to fill normalized_serial for legacy rows.
    Returns number of rows updated.
    """
    rows = frappe.get_all(
        "Instrument Serial Number",
        filters={"normalized_serial": ["in", [None, ""]]},
        fields=["name", "serial"],
        limit=batch_size,
    )
    count = 0
    for r in rows:
        norm = normalize_serial(r.get("serial"))
        frappe.db.set_value("Instrument Serial Number", r["name"], "normalized_serial", norm)
        count += 1
    return count


def bind_erpnext_serial_no(*, isn_name: str, erp_serial_no: str) -> str:
    """
    Link an ERPNext 'Serial No' record to this Instrument Serial Number (optional).
    """
    if not frappe.db.exists("Instrument Serial Number", isn_name):
        raise frappe.DoesNotExistError(isn_name)
    if not frappe.db.exists("Serial No", erp_serial_no):
        raise frappe.DoesNotExistError(erp_serial_no)

    frappe.db.set_value("Instrument Serial Number", isn_name, "erpnext_serial_no", erp_serial_no)
    return isn_name


# --------------------------
# Internals
# --------------------------


def _update_existing_isn(
    isn_name: str,
    *,
    instrument: str | None,
    scan_code: str | None,
    status: str | None,
    serial_source: str | None,
    verification_status: str | None,
) -> None:
    """Selective, safe updates to an existing ISN."""
    doc = frappe.get_doc("Instrument Serial Number", isn_name)

    changed = False

    if instrument and not getattr(doc, "instrument", None):
        doc.instrument = instrument  # type: ignore
        changed = True

    if scan_code and not getattr(doc, "scan_code", None):
        doc.scan_code = scan_code  # type: ignore
        changed = True
    if serial_source and not getattr(doc, "serial_source", None):
        doc.serial_source = serial_source  # type: ignore
        changed = True
    if status and getattr(doc, "status", None) != status:
        doc.status = status  # type: ignore
        changed = True
    if verification_status and not getattr(doc, "verification_status", None):
        doc.verification_status = verification_status  # type: ignore

    if changed:
        doc.save(ignore_permissions=True)


def _try_link_isn_on_instrument(instrument: str, isn_name: str) -> None:
    """
    If Instrument has a Link field to Instrument Serial Number (commonly 'serial_no'),
    set it (non-fatal if field doesn't exist or is Data).
    """
    link_field = "serial_no"
    if not _instrument_has_field(link_field):
        return
    try:
        meta = frappe.get_meta("Instrument")
        df = meta.get_field(link_field)
        if getattr(df, "fieldtype", None) != "Link":
            return
    except Exception:
        return

    current = frappe.db.get_value("Instrument", instrument, link_field)
    if current != isn_name:
        frappe.db.set_value("Instrument", instrument, link_field, isn_name)


def _instrument_has_field(fieldname: str) -> bool:
    try:
        meta = frappe.get_meta("Instrument")
        return any(df.fieldname == fieldname for df in meta.fields)
    except Exception:
        return False
