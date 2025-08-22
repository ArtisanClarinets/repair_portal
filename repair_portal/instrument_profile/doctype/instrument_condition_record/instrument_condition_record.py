# Copyright (c) 2025, your_company_name and contributors
# For license information, please see license.txt
# Path: repair_portal/instrument_profile/doctype/instrument_condition_record/instrument_condition_record.py
# Date: 2024-06-09
# Version: 0.1.1
# Description: Controller for Instrument Condition Record; validates, notifies, updates linked Instrument.
# Dependencies: frappe, Instrument DocType (must have 'instrument' Link field)

from __future__ import annotations

import frappe
from frappe.model.document import Document


class InstrumentConditionRecord(Document):
    """
    Controller for the Instrument Condition Record DocType.
    Manages validation, workflow state transitions, and other business logic.
    """

    def validate(self):
        """
        Validate the document before it is saved.
        - Sets the 'date_of_record' to today if it's not set.
        - Ensures 'notes' are provided if the condition is 'Needs Repair'.
        """
        if not self.date_of_record:
            self.date_of_record = frappe.utils.now()  # type: ignore

        if self.condition == 'Needs Repair' and not self.notes:  # type: ignore
            frappe.throw('Please provide notes for an instrument that needs repair.')

    def before_save(self):
        """
        Logic to run before the document is saved.
        - Sets the owner of the document to the current user.
        """
        self.owner = frappe.session.user  # type: ignore

    def on_submit(self):
        """
        Actions to perform when the document is submitted (docstatus=1).
        """
        frappe.msgprint('Instrument Condition Record submitted successfully.')

    def on_cancel(self):
        """
        Actions to perform when the document is cancelled (docstatus=2).
        """
        frappe.msgprint('Instrument Condition Record has been cancelled.')

    def after_transition(self, transition):
        """
        This method is called after a workflow transition occurs.
        Handles notifications and updates to related documents based on the new state.
        """
        # Notify the inspection team when the record is assigned for inspection.
        if transition.next_state == 'Pending Inspection':
            self.notify_inspection_team()

        # Update the linked instrument's status when the repair is complete.
        if transition.next_state == 'Repair Complete':
            self.update_instrument_status()

    @frappe.whitelist(allow_guest=False)
    def get_instrument_details(self):
        """
        A whitelisted method to get details of the linked instrument.
        This can be called from client-side scripts to fetch data dynamically.
        """
        if not self.instrument:  # type: ignore
            frappe.throw('Instrument not selected.')

        try:
            instrument = frappe.get_doc('Instrument', self.instrument)  # type: ignore
            return {
                'serial_no': instrument.serial_no,  # type: ignore
                'model': instrument.model,  # type: ignore
                'status': instrument.status,  # type: ignore
                # Add any other relevant fields you want to return
            }
        except frappe.DoesNotExistError:
            frappe.throw(f'Instrument {self.instrument} not found.')  # type: ignore

    def notify_inspection_team(self):
        """
        Sends an email notification to the inspection team.
        """
        recipients = ['inspection_team@yourcompany.com']  # Replace with a real email or Role
        instrument_id = getattr(self, 'instrument', None)
        subject = f'Instrument Inspection Required: {instrument_id}'
        message = f"""
        Hello Team,

        Please inspect instrument <strong>{instrument_id or '[Not Set]'}</strong>. 
        You can view the full details in record: {self.name}.

        Thank you.
        """

        frappe.sendmail(recipients=recipients, subject=subject, message=message)
        frappe.msgprint('Notification sent to the inspection team.')

    def update_instrument_status(self):
        """
        Updates the status of the linked instrument document.
        """
        try:
            instrument = frappe.get_doc('Instrument', self.instrument)  # type: ignore
            instrument.status = (
                'Available'  # Assumes 'Instrument' DocType has a 'status' field # type: ignore
            )
            instrument.save()
            frappe.msgprint(
                f"Status of Instrument <strong>{self.instrument}</strong> updated to 'Available'."  # type: ignore
            )
        except frappe.DoesNotExistError:
            frappe.msgprint(
                f'Could not find Instrument {self.instrument} to update its status.',  # type: ignore
            )
