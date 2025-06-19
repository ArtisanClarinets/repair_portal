"""Server-side API methods for Lab module."""

from __future__ import annotations

import frappe


def save_impedance_snapshot(instrument: str, session_type: str, raw_data: str) -> dict:
    """Create an Impedance Snapshot with one peak entry.

    Args:
        instrument: Instrument Profile name.
        session_type: Type of session.
        raw_data: JSON string of sweep results.
    """
    doc = frappe.new_doc("Impedance Snapshot")
    doc.instrument = instrument
    doc.session_type = session_type
    doc.json_data = raw_data
    peak = doc.append("peaks", {})
    peak.frequency = 0
    peak.impedance = 0
    peak.q_factor = 0
    doc.insert(ignore_permissions=True)
    return {"name": doc.name}
