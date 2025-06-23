"""Landing page for the repair portal."""

# File: repair_portal/www/index.py
# Updated: 2025-07-11
# Version: 1.0
# Purpose: Provide the public portal landing page.


def get_context(context):
    """Return base context for the landing page."""
    context.no_cache = True
    context.title = "Clarinet Repair Portal"
    return context
