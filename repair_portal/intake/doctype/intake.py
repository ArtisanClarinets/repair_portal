"""Compatibility shim for the DocType named 'Intake'.

Frappe expects a module at repair_portal.intake.doctype.intake for DocType "Intake".
The actual implementation lives in the clarinet_intake package. To preserve
existing logic and avoid moving files, re-export the primary symbols here.

This file intentionally contains minimal code: imports and aliases only.
"""

from __future__ import annotations

# Re-export the ClarinetIntake controller class and public API so imports
# like `from repair_portal.intake.doctype.intake import ClarinetIntake`
# continue to work for consumers and Frappe's module loader.
from repair_portal.intake.doctype.clarinet_intake.clarinet_intake import (
    ClarinetIntake,
    get_instrument_by_serial,
    get_instrument_inspection_name,
)

__all__ = [
    "ClarinetIntake",
    "get_instrument_by_serial",
    "get_instrument_inspection_name",
]
