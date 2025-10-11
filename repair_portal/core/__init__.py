"""Core cross-module infrastructure for the repair_portal app."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from . import registry

__all__ = ["registry", "lazy_import"]


def lazy_import(path: str) -> Any:
    """Import a dotted path lazily.

    Args:
        path: Dotted Python path to import.

    Returns:
        Imported module or attribute.
    """

    module_path, _, attribute = path.partition(":")
    module = import_module(module_path)
    return getattr(module, attribute) if attribute else module
