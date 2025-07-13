# File: repair_portal/repair_portal/lab/api.py
# Date Updated: 2025-07-13
# Version: 1.4
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
def save_impedance_snapshot(
    instrument: str | None,
    raw_data: str,
    recording_base64: str | None = None,
    filename: str | None = None
) -> dict:
    """
    Create Impedance Snapshot with optional audio processing.
    """
    doc = frappe.new_doc("Impedance Snapshot")
    doc.instrument = instrument

    spectrum = []
    if recording_base64:
        if len(recording_base64) > MAX_RECORDING_SIZE * 1.37:
            raise LabAPIError("Recording too large. Maximum size is 20 MB.")

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
                {"frequency": float(f), "amplitude": float(a)}
                for f, a in zip(freqs, mags, strict=False)
            ]

            doc.json_data = frappe.as_json(spectrum)

        except ImportError:
            raise LabAPIError("Audio processing libraries are not installed. Please contact support.")
        except Exception as e:
            raise LabAPIError("Error processing audio recording.") from e

    doc.insert(ignore_permissions=True)

    if recording_base64 and filename:
        _attach_file(doc, recording_base64, filename)

    return {"name": doc.name}


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_leak_test(*args, **kwargs):
    raise LabAPIError("This API is not yet implemented.")


@frappe.whitelist(allow_guest=False, methods=["POST"])
@frappe.only_for(["Technician"])
def save_intonation_session(*args, **kwargs):
    raise LabAPIError("This API is not yet implemented.")