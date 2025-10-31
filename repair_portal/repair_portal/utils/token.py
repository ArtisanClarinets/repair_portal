"""Token utilities for secure portal access."""
from __future__ import annotations

import hashlib

import frappe


def _hash_value(raw: str, context: str) -> str:
    secret = (frappe.local.conf.get("encryption_key") or "") if getattr(frappe.local, "conf", None) else ""
    payload = f"{raw}:{context}:{secret}".encode()
    return hashlib.sha256(payload).hexdigest()


def generate_token(context: str) -> tuple[str, str]:
    """Generate a random token and deterministic hash for storage."""
    raw = frappe.generate_hash(length=32)
    return raw, _hash_value(raw, context)


def generate_secure_token(prefix: str = "srv") -> str:
    """Return a single-use opaque token for portal links."""
    suffix = frappe.generate_hash(length=24)
    return f"{prefix}-{suffix}"


def verify_token(expected_hash: str | None, candidate: str | None, context: str) -> bool:
    """Validate a candidate token against stored hash."""
    if not expected_hash or not candidate:
        return False
    return _hash_value(candidate, context) == expected_hash


def hash_token(raw: str, context: str) -> str:
    """Hash a raw token using the shared context."""
    return _hash_value(raw, context)
