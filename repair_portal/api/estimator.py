"""Public APIs for the clarinet estimator portal."""

from __future__ import annotations

from typing import List

import frappe
from frappe import _

from repair_portal.service_planning.clarinet_estimator import (
    EstimatorResult,
    UploadedPhoto,
    parse_selections,
    process_estimate_submission,
    serialize_rules_for_portal,
)


@frappe.whitelist()
def get_bootstrap(instrument_family: str | None = None) -> dict:
    """Return estimator metadata for the requested instrument family."""

    frappe.only_for(("Customer", "Technician", "Repair Manager", "System Manager"))
    family = instrument_family or frappe.form_dict.get("instrument_family") or "B\u266d Clarinet"
    return serialize_rules_for_portal(family)


@frappe.whitelist()
def submit() -> dict:
    """Handle estimator submission from the portal."""

    frappe.only_for(("Customer", "Technician", "Repair Manager", "System Manager"))
    data = frappe.form_dict
    instrument_family = data.get("instrument_family")
    if not instrument_family:
        frappe.throw(_("Instrument family is required."))
    serial = data.get("serial")
    condition_score = int(data.get("condition_score") or 0)
    expedite = bool(int(data.get("expedite") or 0))
    selections = parse_selections(data.get("selections"))
    notes = data.get("notes")

    uploads: List[UploadedPhoto] = []
    for file_key, storage in (frappe.request.files or {}).items():
        content = storage.stream.read()
        uploads.append(
            UploadedPhoto(
                filename=storage.filename,
                content=content,
                caption=data.get(f"caption_{file_key}") or storage.filename,
            )
        )

    result: EstimatorResult = process_estimate_submission(
        user=frappe.session.user,
        instrument_family=instrument_family,
        serial=serial,
        condition_score=condition_score,
        expedite=expedite,
        selections=selections,
        notes=notes,
        photo_uploads=uploads,
    )
    return {
        "estimate": result.estimate_name,
        "artifact": result.artifact_name,
        "total": result.total,
        "eta_days": result.eta_days,
        "line_items": result.line_items,
    }
