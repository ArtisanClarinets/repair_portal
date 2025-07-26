# Copyright (c) 2025, Artisan Clarinets AI Division and contributors
# For license information, please see license.txt

import io
import json
from typing import Tuple

import frappe
from frappe.model.document import Document

# --- Optional Heavy Dependencies ---
# The application will function without these, but batch analysis will be disabled.
try:
    import librosa
    import matplotlib
    import numpy as np

    matplotlib.use("Agg")  # Use a non-interactive backend for server-side plotting
    import matplotlib.pyplot as plt

    LIBS_AVAILABLE = True
except ImportError:
    # Set placeholders if libs are not available, to prevent unbound variable errors.
    np = None
    librosa = None
    plt = None
    LIBS_AVAILABLE = False


class ToneIntonationAnalyzer(Document):
    """
    Server-side controller for the Tone & Intonation Analyzer.
    Handles batch audio processing, spectrogram generation, and data persistence.
    """

    # --- Type declarations for DocType fields to satisfy linters like Pylance ---
    # Session Information
    instrument: str
    player: str
    session_datetime: str
    reference_pitch: str
    audio_blob: str
    # Analysis Results
    status: str
    avg_cent_dev: float
    pitch_stability: float
    spectral_cent: float
    harmonics_json: str
    spectrogram_image: str
    # Technician Review
    baseline: int
    notes: str
    # HTML Fields (populated by controller)
    analyzer_html: str
    harmonics_chart_html: str
    help_html: str

    # --- Frappe Document Hooks ---

    def onload(self) -> None:
        """
        Populates read-only HTML fields with content when the form loads.
        This keeps the DocType JSON cleaner and makes the content easier to manage.
        """
        self.set_onload("analyzer_html", self.get_analyzer_tool_html())
        self.set_onload("help_html", self.get_help_html())

    def validate(self) -> None:
        """
        On 'Save', process the attached audio file if it's a new draft.
        """
        if self.is_new() and self.audio_blob and self.status == "Draft":
            if not LIBS_AVAILABLE:
                frappe.msgprint(
                    msg="Audio processing libraries (librosa, numpy, matplotlib) are not installed. Batch analysis is disabled. Please contact your system administrator.",
                    title="Dependencies Missing",
                    indicator="orange",
                )
                return

            self._process_full_audio()

    # --- Core Audio Processing (Batch Mode) ---

    def _process_full_audio(self) -> None:
        """
        Main audio processing pipeline for a saved audio file.
        This extracts all acoustic features and generates visual artifacts.
        """
        try:
            y, sr, a_ref = self._load_audio_from_file()

            # --- Feature Extraction ---
            self._analyze_pitch_and_stability(y, sr, a_ref)
            self._analyze_timbre_and_harmonics(y, sr)

            # --- Visual Artifact Generation ---
            self._generate_and_attach_spectrogram(y, sr)

            self.status = "Analyzed"
            frappe.msgprint("Batch audio analysis complete.", title="Success", indicator="green")

        except Exception as e:
            self.status = "Draft"  # Revert status on any failure
            frappe.log_error(frappe.get_traceback(), "Audio Processing Error")
            frappe.throw(f"Audio analysis failed: {e}")

    def _load_audio_from_file(self) -> tuple[np.ndarray, int, int]:
        """
        Loads the attached audio file from storage into a NumPy array.
        Returns the waveform, sample rate, and reference pitch.
        """
        if not self.audio_blob:
            frappe.throw("No audio file attached.")

        file_doc = frappe.get_doc("File", {"file_url": self.audio_blob})
        file_path = file_doc.get_full_path()  # type: ignore

        # Load audio file using librosa
        y, sr = librosa.load(file_path, sr=None, mono=True)  # type: ignore

        # Parse reference pitch from the form field (e.g., "440 Hz")
        try:
            a_ref = int(self.reference_pitch.split(" ")[0])
        except (ValueError, IndexError):
            a_ref = 440  # Default fallback

        return y, int(sr), a_ref

    def _analyze_pitch_and_stability(self, y: np.ndarray, sr: int, a_ref: int) -> None:
        """
        Analyzes the fundamental frequency (f0) to determine average pitch
        deviation and stability (standard deviation of cents).
        """
        f0, voiced_flag, _ = librosa.pyin(y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr)  # type: ignore
        valid_f0 = f0[voiced_flag & ~np.isnan(f0) & (f0 > 0)]  # type: ignore

        if valid_f0.size > 1:
            # Convert frequencies to cents. `hz_to_cents` gives the absolute cent value
            # from C0. The tuning parameter correctly adjusts this based on A4.
            cents_abs = librosa.hz_to_cents(valid_f0, tuning=a_ref - 440.0)  # type: ignore
            # To get deviation, find the difference from the nearest 100 cents (the perfect note)
            cents_dev = cents_abs - np.round(cents_abs / 100) * 100  # type: ignore

            self.avg_cent_dev = float(np.mean(cents_dev))  # type: ignore
            self.pitch_stability = float(np.std(cents_dev))  # type: ignore
        else:
            self.avg_cent_dev = 0.0
            self.pitch_stability = 0.0
            frappe.msgprint(
                "Could not detect a clear, sustained pitch in the uploaded audio.", indicator="orange"
            )

    def _analyze_timbre_and_harmonics(self, y: np.ndarray, sr: int) -> None:
        """
        Analyzes spectral features related to the tone's timbre, including
        spectral centroid and the relative energy of the first 10 harmonics.
        """
        self.spectral_cent = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))  # type: ignore

        harmonics = librosa.effects.harmonic(y, margin=list(range(1, 11)))  # type: ignore
        stft_harmonics = librosa.stft(harmonics)  # type: ignore
        harmonic_magnitudes, _ = librosa.magphase(stft_harmonics)  # type: ignore

        harmonic_energies = [float(np.sqrt(np.mean(h**2))) for h in harmonic_magnitudes]  # type: ignore

        max_energy = max(harmonic_energies) if harmonic_energies else 1.0
        normalized_energies = [e / max_energy for e in harmonic_energies]

        self.harmonics_json = json.dumps(normalized_energies[:10])

    def _generate_and_attach_spectrogram(self, y: np.ndarray, sr: int) -> None:
        """
        Generates a mel-spectrogram plot, saves it as a PNG, and attaches
        it to the document as a new private File.
        """
        fig, ax = plt.subplots(figsize=(10, 4))  # type: ignore
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)  # type: ignore
        S_dB = librosa.power_to_db(S, ref=np.max(S))  # type: ignore
        img = librosa.display.specshow(S_dB, sr=sr, x_axis="time", y_axis="mel", ax=ax, fmax=8000)  # type: ignore
        fig.colorbar(img, ax=ax, format="%+2.0f dB")
        ax.set_title(f"Mel-Spectrogram for {self.instrument or 'Analysis'}")
        plt.tight_layout()  # type: ignore

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")  # type: ignore
        plt.close(fig)  # type: ignore
        buf.seek(0)

        file_name = f"spectrogram_{self.name.replace(' ', '_')}.png"
        new_file = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": file_name,
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name,
                "attached_to_field": "spectrogram_image",
                "content": buf.getvalue(),
                "is_private": 1,
            }
        )
        new_file.save(ignore_permissions=True)
        self.spectrogram_image = new_file.file_url

    # --- HTML Content Providers ---

    @staticmethod
    def get_analyzer_tool_html() -> str:
        """Returns the static HTML for the live analyzer tool."""
        # This HTML is now injected into the 'analyzer_html' field on the DocType
        return """
            <div id="tone-analyzer-container" class="tone-analyzer-wrapper">
                <div class="analyzer-header">
                    <div class="header-title">
                        <svg ...>...</svg> <!-- SVG content omitted for brevity -->
                        <span>Real-time Analyzer</span>
                    </div>
                    <div class="status-indicator-wrapper">
                        <div id="analyzer-status-light" class="status-light-off"></div>
                        <span id="analyzer-status-text">Idle</span>
                    </div>
                </div>
                <div class="analyzer-body">
                    <div class="gauge-container"><canvas id="tuner-canvas" width="400" height="220"></canvas></div>
                    <div class="readout-container">
                        <div class="note-display-wrapper">
                            <span id="note-display-name">--</span><span id="note-display-octave"></span>
                        </div>
                        <div id="cents-display" class="cents-display-neutral">0 cents</div>
                    </div>
                </div>
                <div class="analyzer-controls">
                    <button id="toggle-analysis-btn" class="btn btn-primary btn-block">
                        <svg ...>...</svg> <!-- SVG content omitted for brevity -->
                        <span>Start Analysis</span>
                    </button>
                </div>
                <div id="analyzer-message-area" class="analyzer-message" style="display: none;"></div>
            </div>
            <div id="harmonics-chart-container" class="mt-4"></div>
        """

    @staticmethod
    def get_help_html() -> str:
        """Returns the static HTML for the help/interpretation section."""
        return """
            <div class="small">
                <h5>What to Look For:</h5>
                <ul>
                    <li><strong>Avg. Cent Deviation:</strong> Ideal is close to 0.</li>
                    <li><strong>Pitch Stability:</strong> Lower is better. High values suggest difficulty holding a steady pitch.</li>
                    <li><strong>Spectral Centroid:</strong> A measure of tonal 'brightness'.</li>
                    <li><strong>Harmonic Energy:</strong> A rich tone has strong energy in the first few harmonics.</li>
                </ul>
            </div>
        """
