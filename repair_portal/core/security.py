"""Security helpers used across custom apps."""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, Iterable

from .registry import Role

try:
    import frappe
except ImportError:  # pragma: no cover - unit tests skip when frappe missing
    frappe = None  # type: ignore

F = Callable[..., Any]


def _coerce_roles(roles: Iterable[Role | str]) -> set[str]:
    return {role.value if isinstance(role, Role) else str(role) for role in roles}


def require_roles(*allowed_roles: Role | str, any_one: bool = True) -> Callable[[F], F]:
    """Ensure the session user has the required roles before executing."""

    allowed = _coerce_roles(allowed_roles)

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):  # type: ignore[misc]
            if frappe is None:
                return func(*args, **kwargs)

            user = frappe.session.user
            user_roles = set(frappe.get_roles(user))
            if any_one:
                if not user_roles.intersection(allowed):
                    frappe.throw("Insufficient role permission.", frappe.PermissionError)
            else:
                if not allowed.issubset(user_roles):
                    frappe.throw("Insufficient role permission.", frappe.PermissionError)
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def rate_limited(key: str, limit: int, window_seconds: int = 60) -> Callable[[F], F]:
    """Rate limit invocations per user per *window_seconds* interval."""

    if limit <= 0:
        raise ValueError("limit must be positive")
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):  # type: ignore[misc]
            if frappe is None:
                return func(*args, **kwargs)

            user = frappe.session.user
            cache = frappe.cache()
            bucket = int(time.time() // window_seconds)
            cache_key = f"rl::{key}::{user}::{bucket}"
            current = cache.get_value(cache_key) or 0
            if not isinstance(current, int):
                current = int(current)
            if current >= limit:
                frappe.throw("Too many requests. Slow down.", frappe.TooManyRequestsError)
            cache.set_value(cache_key, current + 1, expires_in_sec=window_seconds)
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
