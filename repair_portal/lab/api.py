# File: repair_portal/lab/api.py
# Updated: 2025-06-17
# Version: 1.0
# Purpose: Server-side API methods for Lab module.

from __future__ import annotations

import frappe


def _parse_json(data: str) -> list[dict]:
    try:
        return frappe.parse_json(data) or []
    except Exception:  # pragma: no cover - parse errors logged
        frappe.log_error(frappe.get_traceback(), 'Lab API JSON Parse Error')
        return []


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_impedance_snapshot(instrument: str, session_type: str, raw_data: str) -> dict:
    """Persist an Impedance Snapshot document."""
    try:
        peaks = _parse_json(raw_data)
        doc = frappe.new_doc("Impedance Snapshot")
        doc.instrument = instrument
        doc.session_type = session_type
        doc.json_data = raw_data
        for row in peaks or [{}]:
            doc.append(
                "peaks",
                {
                    "frequency": row.get("frequency", 0),
                    "impedance": row.get("impedance", 0),
                    "q_factor": row.get("q_factor", 0),
                },
            )
        doc.insert(ignore_permissions=True)
        return {"name": doc.name}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "save_impedance_snapshot failed")
        frappe.throw("Unable to save impedance snapshot")


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_intonation_session(instrument: str, session_type: str, raw_data: str) -> dict:
    """Persist an Intonation Session document."""
    try:
        notes = _parse_json(raw_data)
        doc = frappe.new_doc("Intonation Session")
        doc.instrument = instrument
        doc.session_type = session_type
        doc.json_data = raw_data
        for row in notes or [{}]:
            doc.append(
                "notes",
                {
                    "note_name": row.get("note_name"),
                    "cents_offset": row.get("cents_offset"),
                    "time_logged": row.get("time_logged"),
                },
            )
        doc.insert(ignore_permissions=True)
        return {"name": doc.name}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "save_intonation_session failed")
        frappe.throw("Unable to save intonation session")


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_leak_test(instrument: str, session_type: str, raw_data: str) -> dict:
    """Persist a Leak Test document."""
    try:
        readings = _parse_json(raw_data)
        doc = frappe.new_doc("Leak Test")
        doc.instrument = instrument
        doc.session_type = session_type
        doc.json_data = raw_data
        for row in readings or [{}]:
            doc.append(
                "readings",
                {
                    "tone_hole": row.get("tone_hole"),
                    "leak_score": row.get("leak_score"),
                    "time_logged": row.get("time_logged"),
                },
            )
        doc.insert(ignore_permissions=True)
        return {"name": doc.name}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "save_leak_test failed")
        frappe.throw("Unable to save leak test")


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_reed_match_result(instrument: str, session_type: str, raw_data: str) -> dict:
    """Persist a Reed Match Result document."""
    try:
        doc = frappe.new_doc("Reed Match Result")
        doc.instrument = instrument
        doc.session_type = session_type
        doc.json_data = raw_data
        doc.insert(ignore_permissions=True)
        return {"name": doc.name}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "save_reed_match_result failed")
        frappe.throw("Unable to save reed match result")


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_tone_fitness(instrument: str, session_type: str, raw_data: str) -> dict:
    """Persist a Tone Fitness document."""
    try:
        entries = _parse_json(raw_data)
        doc = frappe.new_doc("Tone Fitness")
        doc.instrument = instrument
        doc.session_type = session_type
        doc.json_data = raw_data
        for row in entries or [{}]:
            doc.append(
                "entries",
                {
                    "reading_time": row.get("reading_time"),
                    "centroid": row.get("centroid"),
                    "spread": row.get("spread"),
                },
            )
        doc.insert(ignore_permissions=True)
        return {"name": doc.name}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "save_tone_fitness failed")
        frappe.throw("Unable to save tone fitness")

