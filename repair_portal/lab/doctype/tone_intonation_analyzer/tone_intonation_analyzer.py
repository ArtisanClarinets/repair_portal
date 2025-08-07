# File: repair_portal/lab/doctype/tone_intonation_analyzer/tone_intonation_analyzer.py
# Version: 5.0
# Date: 2025-07-23
# Purpose: Enterprise-grade server-side controller for acoustic analysis.

from __future__ import annotations

import base64
import io
import json
from typing import Any

import frappe
from frappe.model.document import Document

# Graceful degradation if heavy DSP libraries are not installed
try:
    import librosa
    import librosa.display
    import matplotlib.pyplot as plt
    import numpy as np

    LIBS_AVAILABLE = True
except ModuleNotFoundError:
    librosa = np = plt = None
    LIBS_AVAILABLE = False


class ToneIntonationAnalyzer(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        audio_blob: DF.Attach | None
        avg_cent_dev: DF.Float
        baseline: DF.Check
        harmonics_json: DF.LongText | None
        instrument: DF.Link
        notes: DF.TextEditor | None
        pitch_stability: DF.Float
        player: DF.Link | None
        reference_pitch: DF.Literal["A=440", "A=441", "A=442"]
        session_datetime: DF.Datetime | None
        spectral_cent: DF.Float
        spectrogram_image: DF.AttachImage | None
        status: DF.Literal[Draft, Analyzed, Reviewed]
    # end: auto-generated types
    """
    Manages the backend logic for tone and intonation analysis, including
    audio processing, spectrogram generation, and baseline management.
    """

    # region: Type Declarations for Document Fields
    audio_blob: str
    reference_pitch: str
    instrument: str
    status: str
    avg_cent_dev: float
    pitch_stability: float
    spectral_cent: float
    harmonics_json: str
    spectrogram_image: str
    baseline: int
    session_datetime: str
    name: str
    doctype: str
    # endregion

    # region: Frappe Document Lifecycle Hooks
    def validate(self) -> None:
        """On 'Save', process the audio if it's a new draft with an audio file."""
        if self.audio_blob and self.status == "Draft" and LIBS_AVAILABLE:
            self._process_audio()
        elif not LIBS_AVAILABLE:
            frappe.log_warning("ToneIntonationAnalyzer: DSP libraries not found. Skipping analysis.")

    # endregion

    # region: Core Audio Processing
    def _process_audio(self) -> None:
        """
        Main audio processing pipeline. Extracts acoustic features from the
        attached audio file and updates the document.
        """
        try:
            y, sr, a_ref = self._load_audio()

            # --- Feature Extraction ---
            self._analyze_pitch(y, sr, a_ref)
            self._analyze_timbre(y, sr)

            # --- Visual Artifact Generation ---
            self._create_spectrogram_image(y, sr)

            self.status = "Analyzed"
        except Exception as e:
            self.status = "Draft"  # Revert status on any failure
            frappe.log_error(frappe.get_traceback(), "Audio Processing Error")
            frappe.throw(f"Audio analysis failed: {e}")

    def _load_audio(self) -> tuple[np.ndarray, int, int]:
        """Loads the audio file, returning the waveform, sample rate, and reference pitch."""
        file_doc = frappe.get_doc("File", {"file_url": self.audio_blob})
        y, sr = librosa.load(file_doc.get_full_path(), sr=None)

        try:
            a_ref = int(self.reference_pitch.split("=")[1])
        except (ValueError, IndexError):
            a_ref = 440
        return y, int(sr), a_ref

    def _analyze_pitch(self, y: np.ndarray, sr: int, a_ref: int) -> None:
        """Analyzes fundamental frequency (f0) to determine pitch deviation and stability."""
        f0, voiced_flag, _ = librosa.pyin(
            y, sr=sr, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
        )
        valid_f0 = f0[voiced_flag & ~np.isnan(f0)]

        if valid_f0.size > 1:
            tuning = a_ref - 440.0
            cents_abs = librosa.hz_to_cents(valid_f0, tuning=tuning)
            cents_dev = cents_abs - np.round(cents_abs / 100) * 100
            self.avg_cent_dev = float(np.mean(cents_dev))
            self.pitch_stability = float(np.std(cents_dev))
        else:
            self.avg_cent_dev = 0.0
            self.pitch_stability = 0.0

    def _analyze_timbre(self, y: np.ndarray, sr: int) -> None:
        """Analyzes spectral features related to the tone's timbre."""
        self.spectral_cent = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

        harmonics_mag = []
        for i in range(1, 11):
            harmonic_y = librosa.effects.harmonic(y=y, margin=i)
            rms_energy = np.mean(librosa.feature.rms(y=harmonic_y))
            harmonics_mag.append(float(rms_energy))
        self.harmonics_json = json.dumps(harmonics_mag)

    def _create_spectrogram_image(self, y: np.ndarray, sr: int) -> None:
        """Generates a spectrogram plot and attaches it to the document."""
        fig, ax = plt.subplots(figsize=(10, 4))
        D = librosa.stft(y)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        img = librosa.display.specshow(S_db, sr=sr, x_axis="time", y_axis="log", ax=ax)
        fig.colorbar(img, ax=ax, format="%+2.0f dB")
        ax.set_title(f"Spectrogram ({self.instrument})")

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)

        file_name = f"spectrogram_{self.name.replace(' ', '_')}.png"
        new_file = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": file_name,
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name,
                "attached_to_field": "spectrogram_image",
                "content": base64.b64encode(buf.read()).decode(),
                "is_private": 1,
            }
        )
        new_file.save(ignore_permissions=True)
        self.spectrogram_image = new_file.file_url

    # endregion

    # region: Whitelisted API Methods for Client-Side
    @frappe.whitelist(allow_guest=False)
    def run_live_analysis(self, chunk: list[float], a_ref: int = 440) -> dict[str, Any]:
        """Analyzes a real-time audio chunk from the browser."""
        if not LIBS_AVAILABLE:
            return {"error": "DSP libraries not available on server."}

        audio = np.array(chunk, dtype=np.float32)
        sr = 44100
        f0 = librosa.yin(audio, fmin=80, fmax=1500, sr=sr)
        valid_f0 = f0[~np.isnan(f0) & (f0 > 0)]

        if valid_f0.size < 5:
            return {"f0": 0.0, "cents_dev": 0.0, "note_name": "--"}

        mean_f0 = float(np.mean(valid_f0))
        tuning = a_ref - 440.0
        note_name = librosa.hz_to_note(mean_f0, tuning=tuning)
        cents_abs = librosa.hz_to_cents(mean_f0, tuning=tuning)
        cents_dev = cents_abs - np.round(cents_abs / 100) * 100

        return {"f0": mean_f0, "cents_dev": cents_dev, "note_name": note_name}

    @frappe.whitelist(allow_guest=False)
    def get_baseline_for_instrument(self, instrument: str) -> dict[str, Any] | None:
        """Fetches the latest approved baseline for a given instrument."""
        baseline = frappe.db.get_value(
            "Tone & Intonation Analyzer",
            filters={"instrument": instrument, "baseline": 1, "docstatus": 1},
            fieldname=["name", "harmonics_json", "avg_cent_dev", "pitch_stability"],
            order_by="session_datetime desc",
            as_dict=True,
        )
        if baseline and baseline.get("harmonics_json"):
            try:
                baseline["harmonics_json"] = json.loads(baseline.get("harmonics_json"))
            except (json.JSONDecodeError, TypeError):
                baseline["harmonics_json"] = []  # Gracefully handle malformed JSON
        return baseline

    # endregion
