# File Header Template
# Relative Path: repair_portal/logger.py
# Last Updated: 2025-07-05
# Version: v1.0
# Purpose: Provide a namespaced, memoised wrapper around ``frappe.logger`` so all
#          modules within the *repair_portal* app emit uniformly-tagged log
#          entries. Ensures Fortune-500-grade observability and simplifies
#          future log-aggregation pipelines.
# Dependencies: frappe (core)

from __future__ import annotations

import functools
from typing import Optional

import frappe


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
@functools.lru_cache(maxsize=None)
def get_logger(suffix: Optional[str] = None) -> "frappe.utils.logger.Logger":
    """Return a memoised, namespaced logger.

    Args:
        suffix: Optional sub-name that will be appended to the base namespace
                (e.g. ``"intake"``, ``"emailer"``).  When omitted, the bare
                namespace ``repair_portal`` is used.

    Returns:
        frappe.utils.logger.Logger: A standard Frappe logger instance.
    """
    namespace = "repair_portal" if not suffix else f"repair_portal.{suffix}"
    return frappe.logger(namespace)
