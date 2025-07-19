# Relative Path: repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.py
# Last Updated: 2025-07-17
# Version: v2.1
# Purpose: Complete Clarinet Initial Setup lifecycle. Adds customer notification on QA pass/submit.
# Dependencies: Frappe >= v15

import frappe
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file


class ClarinetInitialSetup(Document):
    def before_insert(self):
        if not self.technician:
            available = frappe.get_all(
                'User', filters={'role_profile_name': 'Technician'}, fields=['name'], limit=1
            )
            if available:
                self.technician = available[0].name

    def validate(self):
        if not self.intake:
            frappe.throw('Clarinet Intake reference is required.')
        if not self.instrument_profile:
            frappe.throw('Instrument Profile reference is required.')
        # Enforce checklist completion
        for row in self.checklist:
            if not row.completed:
                frappe.throw('All Setup Checklist Items must be completed before submission.')

        # Validate operations: all must be completed
        for op in self.operations_performed:
            if not op.completed:
                frappe.throw('All Setup Operations must be marked as completed before submission.')

        # Require at least one Setup Checklist Item
        if not self.checklist:
            frappe.throw('At least one Setup Checklist Item is required.')

        # Stock validation
        for item in self.materials_used:
            bin_qty = (
                frappe.db.get_value(
                    'Bin', {'item_code': item.item, 'warehouse': item.warehouse}, 'actual_qty'
                )
                or 0
            )
            if item.quantity > bin_qty:
                frappe.throw(f'Insufficient stock for item {item.item}')

        # Auto-load operations if template selected and none added yet
        if self.setup_template and not self.operations_performed:
            self.load_operations_from_template()

    def load_operations_from_template(self):
        """Load default operations from Setup Template."""
        try:
            template = frappe.get_doc('Setup Template', self.setup_template)
            if hasattr(template, 'default_operations'):
                for op in template.default_operations:
                    self.append(
                        'operations_performed',
                        {
                            'operation_type': op.operation_type,
                            'section': op.section,
                            'component_ref': op.component_ref,
                            'details': op.details,
                            'completed': 0,
                        },
                    )
        except Exception:
            frappe.log_error(frappe.get_traceback(), 'Error loading operations from Setup Template')
            frappe.throw('Failed to load default operations. Please contact an administrator.')

    def on_submit(self):
        # Create Material Request
        mr = frappe.new_doc('Material Request')
        mr.material_request_type = 'Material Transfer'
        for item in self.materials_used:
            mr.append(
                'items',
                {
                    'item_code': item.item,
                    'qty': item.quantity,
                    'schedule_date': frappe.utils.nowdate(),
                    'warehouse': item.warehouse,
                },
            )
        mr.insert()
        frappe.msgprint(f'Auto-created Material Request: {mr.name}')

        # Auto-finalize Instrument Profile status
        if self.instrument_profile:
            ip = frappe.get_doc('Instrument Profile', self.instrument_profile)
            ip.db_set('status', 'Ready for Sale')

        # Enqueue PDF generation
        frappe.enqueue(
            method='repair_portal.instrument_setup.doctype.clarinet_initial_setup.clarinet_initial_setup.ClarinetInitialSetup._generate_setup_certificate',
            queue='default',
            job_name=f'Generate Setup Certificate for {self.name}',
            doc=self,
        )

    def _generate_setup_certificate(self):
        """Render HTML → PDF → attach File."""
        html = frappe.render_template(
            'repair_portal/templates/clarinet_initial_setup_certificate.html', {'doc': self}
        )
        pdf = get_pdf(html)
        fname = f'Setup Certificate - {self.name}.pdf'
        save_file(fname, pdf, self.doctype, self.name, is_private=1)


@frappe.whitelist()
def notify_customer_on_completion(docname: str):
    """
    Notify the customer when setup is marked as 'Pass' and submitted.

    Args:
        docname (str): Name of Clarinet Initial Setup

    Returns:
        None
    """
    try:
        setup = frappe.get_doc('Clarinet Initial Setup', docname)
        if not setup.instrument_profile:
            return
        profile = frappe.get_doc('Instrument Profile', setup.instrument_profile)
        # Lookup owner/customer from profile or intake
        customer_email = None
        if profile.owner:
            customer_email = frappe.db.get_value('User', profile.owner, 'email')
        if not customer_email and getattr(profile, 'customer', None):
            customer_email = frappe.db.get_value('Customer', profile.customer, 'email_id')
        if not customer_email and getattr(setup, 'intake', None):
            intake = frappe.get_doc('Clarinet Intake', setup.intake)
            if getattr(intake, 'owner', None):
                customer_email = frappe.db.get_value('User', intake.owner, 'email')

        if not customer_email:
            frappe.log_error('No customer email found for setup: ' + docname)
            return

        # Compose message
        subject = f'Your Instrument Setup is Complete – {setup.name}'
        message = f'Dear customer,<br>Your clarinet has completed initial setup and passed QA.<br>Thank you!<br>— The Artisan Clarinets Team'
        frappe.sendmail(recipients=[customer_email], subject=subject, message=message)

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            'notify_customer_on_completion failed for Clarinet Initial Setup',
        )
