# File: repair_portal/repair_portal/lab/api.py
# Date Updated: 2025-06-29
# Version: 1.2
# Purpose: APIs to save lab measurement sessions, recordings, and inspection reports

import base64
import math

import frappe

# ────────── UTILITY FUNCTIONS ──────────


def _attach_file(parent_doc, b64, fname):
    file_doc = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": fname,
            "attached_to_doctype": parent_doc.doctype,
            "attached_to_name": parent_doc.name,
            "content": base64.b64decode(b64),
        }
    )
    file_doc.save(ignore_permissions=True)


def freq_to_note(freq):
    if not freq:
        return "—"
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    n = round(12 * math.log2(freq / 440.0) + 57)
    return note_names[n % 12] + str(n // 12 - 1)


def calc_cents(freq):
    if not freq:
        return 0
    n = 12 * math.log2(freq / 440.0)
    nearest = round(n)
    return (n - nearest) * 100


# ────────── API FUNCTIONS ──────────


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_intonation_session(
    instrument: str | None,
    player: str | None,
    session_type: str,
    raw_data: str,
    recording_base64: str | None = None,
    filename: str | None = None,
) -> dict:
    """
    Save an Intonation Session with note readings and optional recording.
    """
    peaks = frappe.parse_json(raw_data)

    doc = frappe.new_doc("Intonation Session")
    doc.instrument = instrument
    doc.player = player
    doc.session_type = session_type
    doc.json_data = raw_data

    for row in peaks:
        doc.append(
            "notes",
            {
                "note_name": freq_to_note(row["note_hz"]),
                "cents_offset": calc_cents(row["note_hz"]),
                "time_logged": row["reading_time"],
            },
        )

    doc.insert(ignore_permissions=True)

    if recording_base64 and filename:
        _attach_file(doc, recording_base64, filename)

    return {"name": doc.name}


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_impedance_snapshot(
    instrument: str | None, raw_data: str, recording_base64: str | None = None, filename: str | None = None
) -> dict:
    """
    Create Impedance Snapshot with optional audio processing.
    """
    doc = frappe.new_doc("Impedance Snapshot")
    doc.instrument = instrument

    spectrum = []
    if recording_base64:
        try:
            import io

            import librosa
            import numpy as np
            import soundfile as sf

            wav_bytes = base64.b64decode(recording_base64)
            wav_buffer = io.BytesIO(wav_bytes)
            y, sr = sf.read(wav_buffer)

            S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
            freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
            mags = np.mean(S, axis=1)
            spectrum = [
                {"frequency": float(f), "amplitude": float(a)} for f, a in zip(freqs, mags, strict=False)
            ]

            doc.json_data = frappe.as_json(spectrum)

        except Exception:
            frappe.log_error(frappe.get_traceback(), "Impedance Processing Failed")

    doc.insert(ignore_permissions=True)

    if recording_base64 and filename:
        _attach_file(doc, recording_base64, filename)

    return {"name": doc.name}


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_inspection_report(
    instrument: str | None,
    inspection_type: str,
    inspection_data: str,
    recording_base64: str | None = None,
    filename: str | None = None,
) -> dict:
    """
    Save an inspection report with optional recording.
    """
    doc = frappe.new_doc("Inspection Report")
    doc.instrument = instrument
    doc.inspection_type = inspection_type
    doc.json_data = inspection_data

    doc.insert(ignore_permissions=True)

    if recording_base64 and filename:
        _attach_file(doc, recording_base64, filename)

    return {"name": doc.name}


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_leak_test(instrument: str | None, readings_json: str) -> dict:
    """
    Save Leak Test data and child decay readings.
    """
    try:
        readings = frappe.parse_json(readings_json)
    except Exception:
        frappe.throw("Invalid readings JSON.")

    if not readings:
        frappe.throw("No readings provided.")

    doc = frappe.new_doc("Leak Test")
    doc.instrument = instrument
    doc.json_data = readings_json

    for row in readings:
        doc.append("readings", {"time_ms": row.get("t_ms"), "amplitude": row.get("rms")})

    doc.insert(ignore_permissions=True)

    return {"name": doc.name}


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_tone_fitness(instrument: str | None, readings_json: str) -> dict:
    """
    Save Tone Fitness data and child entries.
    """
    try:
        readings = frappe.parse_json(readings_json)
    except Exception:
        frappe.throw("Invalid readings JSON.")

    if not readings:
        frappe.throw("No readings provided.")

    doc = frappe.new_doc("Tone Fitness")
    doc.instrument = instrument
    doc.json_data = readings_json

    for row in readings:
        doc.append("entries", {"time_ms": row.get("t_ms"), "amplitude": row.get("rms")})

    doc.insert(ignore_permissions=True)

    return {"name": doc.name}
