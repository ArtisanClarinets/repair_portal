"""Clarinet Pad Map Artifact controller."""

from __future__ import annotations

from typing import Iterable

from frappe import _, throw
from frappe.model.document import Document


class ClarinetPadMapArtifact(Document):
    """Immutable summary of a portal estimator submission."""

    def validate(self) -> None:  # noqa: D401
        if not self.instrument_serial:
            throw(_("Instrument Serial is required."))
        if self.condition_score is None:
            throw(_("Condition Score is required."))
        if self.condition_score < 0 or self.condition_score > 100:
            throw(_("Condition Score must be between 0 and 100."))
        if not self.selections:
            throw(_("At least one selection is required."))
        if not self.photos:
            throw(_("At least one photo is required."))
        self._validate_selection_totals(self.selections)  # type: ignore[arg-type]

    def _validate_selection_totals(self, rows: Iterable[Document]) -> None:
        for row in rows:
            if row.line_total is None or row.line_total < 0:
                throw(_("Selection line totals must be provided."))
