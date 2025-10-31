"""Controller for Service Plan DocType."""
from __future__ import annotations

from typing import Final

import frappe
from frappe import _
from frappe.model.document import Document

_INTERACTION_TYPE: Final[str] = "Service Plan"


class ServicePlan(Document):
    """Handle lifecycle automation for service plans."""

    def on_submit(self) -> None:
        """Log the plan against the linked Instrument Profile when submitted."""
        profile_name = (self.instrument or "").strip()
        if not profile_name:
            return

        if not frappe.db.exists("Instrument Profile", profile_name):
            frappe.throw(
                _("Instrument Profile '{0}' was not found. Please select a valid profile.").format(
                    profile_name
                )
            )

        profile = frappe.get_doc("Instrument Profile", profile_name)
        profile.append(
            "interaction_logs",
            {
                "interaction_type": _INTERACTION_TYPE,
                "reference_doctype": self.doctype,
                "reference_name": self.name,
                "date": self.plan_date,
                "notes": self._interaction_notes(),
            },
        )
        profile.save(ignore_permissions=True)

    def _interaction_notes(self) -> str:
        """Choose the best available summary text for the interaction log."""
        for field in ("plan_summary", "notes"):
            value = (getattr(self, field, None) or "").strip()
            if value:
                return value
        return ""
