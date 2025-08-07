# File Header Template
# Relative Path: repair_portal/lab/doctype/lab_intonation_session/lab_intonation_session.py
# Last Updated: 2025-07-24
# Version: v1.0
# Purpose: Controller for storing intonation measurement sessions and associated acoustic analysis
# Dependencies: Instrument, Lab Note Entry

import frappe
from frappe.model.document import Document


class LabIntonationSession(Document):
    """
    Stores data for intonation analysis, including average impedance and spectrogram output
    for each instrument session.
    """
    def validate(self):
        # Ensure instrument is selected
        if not self.instrument:
            frappe.throw("Please select an instrument for this session.")

    def on_submit(self):
        # Example future hook: process spectrogram or finalize metrics
        frappe.logger().info(f"Lab Intonation Session {self.name} submitted.")