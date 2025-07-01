# File: repair_portal/repair_portal/lab/api.py
# Date Updated: 2025-07-01
# Version: 1.3
# Purpose: APIs with size checks and safe imports

import base64
import math

import frappe

MAX_RECORDING_SIZE = 20 * 1024 * 1024  # 20MB


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
        if len(recording_base64) > MAX_RECORDING_SIZE * 1.37:  # Base64 overhead ~37%
            frappe.throw("Recording too large. Maximum size is 20 MB.")

        try:
            import io

            try:
                import librosa
                import numpy as np
                import soundfile as sf
            except ImportError:
                frappe.throw("Audio processing libraries are not installed. Please contact support.")

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
            frappe.throw("Error processing audio recording.")

    doc.insert(ignore_permissions=True)

    if recording_base64 and filename:
        _attach_file(doc, recording_base64, filename)

    return {"name": doc.name}
