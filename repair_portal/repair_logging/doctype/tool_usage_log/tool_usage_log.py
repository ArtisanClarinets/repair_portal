"""
repair_logging/doctype/tool_usage_log/tool_usage_log.py
Tool Usage Log
Version 1.0
Last Updated: 2025-06-09

Tracks technician tool usage during repair tasks. Links tools to users and adds usage notes.
"""

from __future__ import annotations

from frappe.model.document import Document


class ToolUsageLog(Document):
	pass
