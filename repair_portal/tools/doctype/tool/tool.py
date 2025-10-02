# File: repair_portal/tools/doctype/tool/tool.py
# Date Updated: 2025-07-17
# Version: v1.2
# Purpose: Tracks tool metadata, serviceability, calibration lifecycle, and ERPNext Asset sync. Automated calibration notifications.
from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, nowdate


class Tool(Document):
    def validate(self):
        if self.requires_calibration and not self.next_due:  # type: ignore
            frappe.throw("Please set 'Next Calibration Due' for tools requiring calibration.")

    def on_submit(self):
        """
        On submit, auto-create ERPNext Asset if not linked (optional).
        """
        try:
            if not self.asset:  # type: ignore
                # Optionally auto-create asset (uncomment if desired)
                pass
        except Exception:
            frappe.log_error(frappe.get_traceback(), 'Tool: on_submit asset sync failed')


def send_calibration_due_notifications(days_ahead=7):
    """
    Scheduled: Sends notification for tools with calibration due within X days.
    """
    try:
        today = nowdate()
        cutoff = add_days(today, days_ahead)
        tools = frappe.get_all(
            'Tool',
            filters={
                'requires_calibration': 1,
                'next_due': ('<=', cutoff),
                'workflow_state': ['!=', 'Retired'],
            },
            fields=['name', 'tool_name', 'next_due', 'owner', 'asset'],
        )
        for t in tools:
            doc = frappe.get_doc('Tool', t.name)
            recipients = [doc.owner]
            # Optionally add Service Manager(s) or custom logic
            subject = f'Calibration Due Soon: {doc.tool_name}'  # type: ignore
            message = (
                f'Tool <b>{doc.tool_name}</b> requires calibration by <b>{doc.next_due}</b>.\n'  # type: ignore
                'Please schedule or record calibration in the system.'
            )
            try:
                frappe.sendmail(recipients=recipients, subject=subject, message=message)
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(), f'Tool Calibration notification failed: {doc.name}'
                )
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'send_calibration_due_notifications: bulk failure')
