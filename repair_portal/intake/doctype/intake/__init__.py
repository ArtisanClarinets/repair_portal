"""Package shim for DocType 'Intake'.

This package exposes a submodule `intake` which re-exports the real
implementation living under clarinet_intake. Frappe may try to import
`repair_portal.intake.doctype.intake.intake` or treat `intake` as a package;
providing this package ensures both import styles work.
"""

from importlib import import_module
from types import ModuleType
from typing import Any

# Lazy import the real module to avoid eager import-time errors during bench commands
_real_mod_name = "repair_portal.intake.doctype.clarinet_intake.clarinet_intake"


def _load_real() -> ModuleType:
    return import_module(_real_mod_name)


def __getattr__(name: str) -> Any:  # pragma: no cover - thin shim
    """Delegate attribute access to the real clarinet_intake module."""
    mod = _load_real()
    return getattr(mod, name)


def __dir__() -> list[str]:
    mod = _load_real()
    return list(globals().keys()) + [n for n in dir(mod) if not n.startswith("_")]


# For the case where code does `from repair_portal.intake.doctype.intake import ClarinetIntake`
# make the common symbols available at package import time.
_mod = _load_real()
for _sym in ("ClarinetIntake", "get_instrument_by_serial", "get_instrument_inspection_name"):
    if hasattr(_mod, _sym):
        globals()[_sym] = getattr(_mod, _sym)

__all__ = ["ClarinetIntake", "get_instrument_by_serial", "get_instrument_inspection_name"]
