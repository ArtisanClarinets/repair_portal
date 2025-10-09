"""Submodule shim so imports like

    import repair_portal.intake.doctype.intake.intake

succeed. Delegates to the real clarinet_intake implementation.
"""

from __future__ import annotations

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
