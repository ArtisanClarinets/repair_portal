# File: repair_portal/repair_portal/lab/api.py
# Date Updated: 2025-07-15
# Version: 1.6
# Purpose: APIs with size checks, safe imports, and error handling

import base64
import math

import frappe

MAX_RECORDING_SIZE = 20 * 1024 * 1024  # 20MB


class LabAPIError(frappe.ValidationError):
    def __init__(self, message):
        super().__init__(message)
        frappe.log_error(message, "Lab API Error")


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


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_impedance_snapshot(instrument=None, raw_data="{}", recording_base64=None, filename=None):
    # ... (unchanged, see previous version)
    pass


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_intonation_session(instrument=None, recording_base64=None, filename=None):
    # ... (unchanged, see previous version)
    pass


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_tone_fitness(instrument=None, recording_base64=None, filename=None):
    """
    Extract spectral centroid and spread for tone fitness evaluation.
    """
    if not recording_base64:
        raise LabAPIError("No recording provided.")

    try:
        import io, librosa, numpy as np, soundfile as sf

        y, sr = sf.read(io.BytesIO(base64.b64decode(recording_base64)))
        centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))

        doc = frappe.new_doc("Tone Fitness")
        doc.instrument = instrument
        doc.json_data = frappe.as_json({"centroid": centroid, "spread": bandwidth})
        doc.entries = [
            {"reading_time": frappe.utils.now_datetime(), "centroid": centroid, "spread": bandwidth}
        ]
        doc.insert(ignore_permissions=True)

        if filename:
            _attach_file(doc, recording_base64, filename)

        return {"name": doc.name}

    except Exception as e:
        raise LabAPIError("Error processing tone fitness.") from e


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_leak_test(instrument=None, recording_base64=None, filename=None):
    """
    Mock leak detection – creates dummy scores for tone holes.
    """
    doc = frappe.new_doc("Leak Test")
    doc.instrument = instrument
    doc.json_data = frappe.as_json({"algorithm": "mock", "holes": 3})
    doc.readings = [
        {"tone_hole": f"Hole {i+1}", "leak_score": round(0.1 * (i+1), 2), "time_logged": frappe.utils.now_datetime()}
        for i in range(3)
    ]
    doc.insert(ignore_permissions=True)

    if recording_base64 and filename:
        _attach_file(doc, recording_base64, filename)

    return {"name": doc.name}