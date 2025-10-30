"""Barcode and QR helpers for Repair Portal doctypes."""
from __future__ import annotations

import base64
from io import BytesIO
from typing import Iterable

import frappe
from frappe import _
from frappe.utils import now_datetime

try:  # pragma: no cover - import guard depends on frappe distribution
    from frappe.utils import qr_code as frappe_qr  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - optional dependency path
    frappe_qr = None

try:  # pragma: no cover - optional dependency
    import qrcode
except Exception:  # pragma: no cover - optional dependency path
    qrcode = None


def _ensure_barcode(doc: frappe.Document, fieldname: str, fallback_fields: Iterable[str] = ()) -> str:
    existing = (doc.get(fieldname) or "").strip()
    if existing:
        return existing

    for candidate in fallback_fields:
        value = (doc.get(candidate) or "").strip()
        if value:
            doc.set(fieldname, value)
            return value

    # Use permanent name when available, otherwise generate a hash prefix.
    name = (doc.name or "").strip()
    if name and not name.lower().startswith("new "):
        doc.set(fieldname, name)
        return name

    generated = f"RP-{frappe.generate_hash(length=12)}"
    doc.set(fieldname, generated)
    return generated


def ensure_repair_order_barcode(doc: frappe.Document, _event: str | None = None) -> None:
    """Guarantee repair orders always have a scannable barcode string."""
    _ensure_barcode(doc, "barcode", ("repair_request", "instrument"))
    if not doc.get("scheduled_start"):
        doc.scheduled_start = now_datetime()


def ensure_clarinet_intake_barcode(doc: frappe.Document, _event: str | None = None) -> None:
    """Ensure intake tickets receive a deterministic barcode."""
    _ensure_barcode(doc, "barcode", ("instrument", "customer"))


def ensure_instrument_barcode(doc: frappe.Document, _event: str | None = None) -> None:
    """Backfill instrument barcode using serial number when present."""
    _ensure_barcode(doc, "barcode", ("serial_no",))


def _generate_qr_image(value: str):
    if frappe_qr and hasattr(frappe_qr, "make_qr_code"):
        return frappe_qr.make_qr_code(value)
    if qrcode:
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(value)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")
    frappe.throw(_("QR code generation library is unavailable."))
    raise RuntimeError("QR code generation library is unavailable.")


def qr_data_uri(value: str | None) -> str:
    if not value:
        return ""
    image = _generate_qr_image(value)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"
