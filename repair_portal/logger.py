# Relative Path: repair_portal/logger.py
# Last Updated: 2025-08-10
# Version: v1.1
# Purpose: Provide a namespaced, memoised wrapper around ``frappe.logger`` so all
#          modules within the *repair_portal* app emit uniformly-tagged log
#          entries. Ensures Fortune-500-grade observability and simplifies
#          future log-aggregation pipelines.
# Dependencies: frappe (core)

from __future__ import annotations

import functools
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any

import frappe
from frappe.utils import get_site_path



####################### ——OLD—— #######################

# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
@functools.cache
def get_logger(suffix: str | None = None) -> frappe.utils.logger.Logger: # type: ignore
    """Return a memoised, namespaced logger.

    Args:
        suffix: Optional sub-name that will be appended to the base namespace
                (e.g. ``"intake"``, ``"emailer"``).  When omitted, the bare
                namespace ``repair_portal`` is used.

    Returns:
        frappe.utils.logger.Logger: A standard Frappe logger instance.
    """
    namespace = "repair_portal" if not suffix else f"repair_portal.{suffix}"
    return frappe.log_error(namespace) # pyright: ignore[reportAttributeAccessIssue]
########################### ——OLD—— ###########################

# --------------------------------------------------------------------------- #
#  Configuration
# --------------------------------------------------------------------------- #

# Max size per log file (bytes) and number of backups to retain
_DEBUG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_ERROR_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_BACKUP_COUNT = 10

# Filenames inside the logs directory
_DEBUG_FILENAME = "repair_portal.debug.log"
_ERROR_FILENAME = "repair_portal.error.log"

# Default log level for our base loggers
_BASE_LEVEL = logging.DEBUG

# Whether to also echo to stderr (useful during local dev)
_ECHO_TO_STDERR = os.environ.get("REPAIR_PORTAL_LOG_STDERR", "0") in ("1", "true", "True")


# --------------------------------------------------------------------------- #
#  Utility: resolve & create logs directory with fallbacks
# --------------------------------------------------------------------------- #

def _resolve_logs_dir() -> str:
    """
    Prefer <app_root>/repair_portal/logs.
    Fallback to <site>/logs/repair_portal, then /tmp/repair_portal-logs.
    Always ensures the directory exists.
    """
    # This file lives at <app_root>/repair_portal/repair_portal/logger.py
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    primary = os.path.join(app_root, "repair_portal", "logs")

    tried = []

    for candidate in (primary,):
        tried.append(candidate)
        try:
            os.makedirs(candidate, exist_ok=True)
            return candidate
        except Exception:
            continue

    # Fallback: site-specific logs dir
    try:
        site_logs = os.path.join(get_site_path("logs"), "repair_portal")
        tried.append(site_logs)
        os.makedirs(site_logs, exist_ok=True)
        return site_logs
    except Exception:
        pass

    # Last resort: /tmp
    tmp_dir = "/tmp/repair_portal-logs"
    tried.append(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    # Inform once on stderr to help operators discover the location
    print(
        "repair_portal.logger: using fallback logs directory. Tried: "
        + " | ".join(tried),
        file=sys.stderr,
    )
    return tmp_dir


@functools.lru_cache(maxsize=1)
def _logs_dir() -> str:
    return _resolve_logs_dir()


# --------------------------------------------------------------------------- #
#  Context: enrich logs with site/user/request/job when available
# --------------------------------------------------------------------------- #

def _current_context() -> Dict[str, Any]:
    site = getattr(frappe.local, "site", None) if hasattr(frappe, "local") else None
    user = None
    try:
        user = frappe.session.user if getattr(frappe, "session", None) else None
    except Exception:
        user = None

    # Best-effort IDs for jobs/requests if present
    req_id = getattr(getattr(frappe.local, "_request_ctx", None), "request_id", None) \
             or getattr(frappe.local, "request_id", None) if hasattr(frappe, "local") else None
    job_id = getattr(frappe.local, "task_id", None) if hasattr(frappe, "local") else None

    return {
        "site": site or "-",
        "user": user or "-",
        "request_id": req_id or "-",
        "job": job_id or "-",
    }


class _ContextAdapter(logging.LoggerAdapter):
    """Injects Frappe contextual fields into every log record."""

    def process(self, msg, kwargs):
        extra = kwargs.get("extra") or {}
        # Do not overwrite explicit extras supplied by caller
        base = _current_context()
        for k, v in base.items():
            extra.setdefault(k, v)
        kwargs["extra"] = extra
        return msg, kwargs


# --------------------------------------------------------------------------- #
#  Handler/formatter factory (dedup-safe)
# --------------------------------------------------------------------------- #

@functools.lru_cache(maxsize=None)
def _build_logger(namespace: str) -> logging.Logger:
    """
    Create (or fetch) a Python logger with rotating file handlers for DEBUG and ERROR.
    Idempotent: repeated calls won't attach duplicate handlers.
    """
    logger = logging.getLogger(namespace)
    logger.setLevel(_BASE_LEVEL)
    logger.propagate = False  # keep our formatting clean; Frappe/root can still log separately

    # If already configured, return as-is
    if logger.handlers:
        return logger

    logs_dir = _logs_dir()
    debug_path = os.path.join(logs_dir, _DEBUG_FILENAME)
    error_path = os.path.join(logs_dir, _ERROR_FILENAME)

    # Format includes site/user/job/request for ops visibility
    fmt = (
        "%(asctime)s %(levelname)s [%(name)s] "
        "[site=%(site)s user=%(user)s job=%(job)s req=%(request_id)s] "
        "%(message)s"
    )
    formatter = logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S%z")

    # DEBUG (all levels) → repair_portal.debug.log
    debug_handler = RotatingFileHandler(
        debug_path, maxBytes=_DEBUG_MAX_BYTES, backupCount=_BACKUP_COUNT, encoding="utf-8"
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    # ERROR+ → repair_portal.error.log
    error_handler = RotatingFileHandler(
        error_path, maxBytes=_ERROR_MAX_BYTES, backupCount=_BACKUP_COUNT, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # Optional STDERR echo for local dev / CI visibility
    if _ECHO_TO_STDERR:
        stderr_handler = logging.StreamHandler(stream=sys.stderr)
        stderr_handler.setLevel(logging.INFO)
        stderr_handler.setFormatter(formatter)
        logger.addHandler(stderr_handler)

    # Also register with Frappe’s logger namespace so Error Log links stay useful
    try:
        # This returns a stdlib logger pre-wired by Frappe; we align its level.
        frappe_logger = frappe.logger(namespace)  # type: ignore[attr-defined]
        frappe_logger.setLevel(_BASE_LEVEL)
        # Don’t add our handlers to the frappe logger (to avoid duplicates),
        # but keep it non-propagating for cleaner output.
        frappe_logger.propagate = False
    except Exception:
        # If frappe.logger isn’t available yet (early import), ignore.
        pass

    return logger


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #

@functools.cache
def get_logger(suffix: Optional[str] = None) -> logging.LoggerAdapter:
    """
    Return a memoised, namespaced logger adapter.

    Usage:
        from repair_portal.logger import get_logger
        log = get_logger("intake")
        log.info("Created order", extra={"order_id": "ORD-0001"})
        try:
            ...
        except Exception:
            log.exception("Failed to process order")  # full traceback to error.log & debug.log

    Args:
        suffix: Optional sub-namespace (e.g. "intake", "emailer").
                If omitted, the bare namespace "repair_portal" is used.

    Returns:
        logging.LoggerAdapter with contextual enrichment (site/user/request/job).
    """
    namespace = "repair_portal" if not suffix else f"repair_portal.{suffix}"
    base = _build_logger(namespace)
    return _ContextAdapter(base, {})


def exception_to_logs(msg: str, *args, suffix: Optional[str] = None, **kwargs) -> None:
    """
    Convenience helper to log the *current* exception with traceback.
    Call inside an `except` block.

        try:
            ...
        except Exception:
            exception_to_logs("Failed to seed templates", suffix="seeder")

    """
    log = get_logger(suffix)
    log.error(msg, *args, exc_info=True, **kwargs)


def audit(msg: str, *args, suffix: Optional[str] = None, **kwargs) -> None:
    """
    Convenience helper to write a high-signal INFO line (e.g., migrations).
    """
    get_logger(suffix).info("[AUDIT] " + msg, *args, **kwargs)


def debug(msg: str, *args, suffix: Optional[str] = None, **kwargs) -> None:
    """Shorthand for DEBUG logs."""
    get_logger(suffix).debug(msg, *args, **kwargs)


def error(msg: str, *args, suffix: Optional[str] = None, **kwargs) -> None:
    """Shorthand for ERROR logs."""
    get_logger(suffix).error(msg, *args, **kwargs)


def warn(msg: str, *args, suffix: Optional[str] = None, **kwargs) -> None:
    """Shorthand for WARNING logs."""
    get_logger(suffix).warning(msg, *args, **kwargs)


def info(msg: str, *args, suffix: Optional[str] = None, **kwargs) -> None:
    """Shorthand for INFO logs."""
    get_logger(suffix).info(msg, *args, **kwargs)


# --------------------------------------------------------------------------- #
#  Decorator: auto-log exceptions with tracebacks (opt-in)
# --------------------------------------------------------------------------- #

def log_exceptions(suffix: Optional[str] = None, reraise: bool = False):
    """
    Decorator that logs exceptions (with traceback) using our logger.
    If reraise=True, the exception is rethrown after logging.

    @log_exceptions("seeder", reraise=True)
    def seed():
        ...
    """
    def _decorator(fn):
        logger = get_logger(suffix)
        @functools.wraps(fn)
        def _wrapped(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception:
                logger.exception("Unhandled exception in %s", fn.__name__)
                if reraise:
                    raise
        return _wrapped
    return _decorator
