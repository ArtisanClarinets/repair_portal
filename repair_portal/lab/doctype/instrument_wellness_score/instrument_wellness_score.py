# File: repair_portal/lab/doctype/instrument_wellness_score/instrument_wellness_score.py
# Updated: 2025-06-29
# Version: 1.0
# Purpose: Automatically compute an instrument's wellness score from lab data

import frappe
from frappe.model.document import Document


class InstrumentWellnessScore(Document):

    def validate(self):
        """
        On save, calculate individual and overall scores.
        """
        if not self.instrument:
            frappe.throw("Instrument is required.")

        self.intonation_score = self._calculate_intonation_score()
        self.impedance_score = self._calculate_impedance_score()
        self.leak_score = self._calculate_leak_score()
        self.tone_score = self._calculate_tone_score()

        # Weighted average (weights can be adjusted)
        self.overall_score = (
            0.3 * self.intonation_score
            + 0.3 * self.impedance_score
            + 0.2 * self.leak_score
            + 0.2 * self.tone_score
        )

    def _calculate_intonation_score(self):
        """
        Average cents deviation across last 5 intonation sessions.
        Lower deviation = higher score.
        """
        readings = frappe.db.sql(
            """
            SELECT json_data
            FROM `tabIntonation Session`
            WHERE instrument = %s
            ORDER BY creation DESC
            LIMIT 5
        """,
            self.instrument,
            as_dict=True,
        )

        if not readings:
            return 50

        deviations = []
        for row in readings:
            notes = frappe.parse_json(row.json_data)
            for note in notes:
                deviations.append(abs(note.get("cents_offset", 0)))

        if not deviations:
            return 50

        avg_dev = sum(deviations) / len(deviations)
        score = max(0, 100 - avg_dev)
        return round(score, 2)

    def _calculate_impedance_score(self):
        """
        Simpler: count snapshots in last 5 records.
        More impedance data = higher score.
        """
        count = frappe.db.count("Impedance Snapshot", {"instrument": self.instrument})
        return min(100, count * 20)

    def _calculate_leak_score(self):
        """
        Recent leak test status.
        Less leakage = higher score.
        """
        latest = frappe.db.get_value(
            "Leak Test", {"instrument": self.instrument}, ["leak_rate"], order_by="creation DESC"
        )
        if latest is None:
            return 50

        leak_rate = float(latest or 0)
        score = max(0, 100 - leak_rate * 50)
        return round(score, 2)

    def _calculate_tone_score(self):
        """
        Average tone fitness score in last 5 records.
        """
        entries = frappe.db.sql(
            """
            SELECT avg(overall_score)
            FROM `tabTone Fitness`
            WHERE instrument = %s
        """,
            self.instrument,
        )
        avg = entries[0][0] if entries and entries[0][0] else 50
        return round(avg, 2)

    def on_submit(self):
        self._calculate_intonation_score()
        self._calculate_impedance_score()
        self._calculate_leak_score()
        self._calculate_tone_score()
