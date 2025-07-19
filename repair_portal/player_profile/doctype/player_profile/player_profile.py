# Relative Path: repair_portal/player_profile/doctype/player_profile/player_profile.py
# Last Updated: 2025-07-17
# Version: v1.6
# Purpose: WebsiteGenerator for Player Profile with COPPA checks, visibility logic, route formatting, auto-updating log tracker, and parental notification on compliance block.
# Dependencies: Customer, Instrument Profile, Repair Log, Clarinet Inspection, Setup Log, Leak Test, etc.

import frappe
from frappe.website.website_generator import WebsiteGenerator
from datetime import datetime


class PlayerProfile(WebsiteGenerator):
    website = frappe._dict(
        condition_field='published', page_title_field='player_name', route='route'
    )

    def autoname(self):
        if not self.route and self.player_name and self.customer:
            scrubbed_name = frappe.scrub(self.player_name)
            self.route = f'players/{self.customer}-{scrubbed_name}'

    def validate(self):
        if not self.customer:
            frappe.throw('Player Profile must be linked to a Customer.')

        if self.date_of_birth:
            try:
                age = (datetime.now().date() - self.date_of_birth).days // 365
                if age < 13:
                    self.block_marketing_emails()
            except Exception:
                frappe.log_error(frappe.get_traceback(), 'PlayerProfile.validate failed on DOB')

    def block_marketing_emails(self):
        try:
            if self.email:
                frappe.db.set_value('Email Group Member', {'email': self.email}, 'unsubscribed', 1)
            # Notify parent/client user if available
            parent_user = frappe.db.get_value('Customer', self.customer, 'linked_user')
            if parent_user:
                parent_email = frappe.db.get_value('User', parent_user, 'email')
                if parent_email:
                    subject = f'Profile Marketing Blocked for {self.player_name}'
                    message = f'Dear Parent/Guardian,<br>Due to compliance, marketing emails for {self.player_name} have been blocked (age under 13). No action is required.<br>Thank you!<br>— The Artisan Clarinets Team'
                    frappe.sendmail(recipients=[parent_email], subject=subject, message=message)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(), 'PlayerProfile: block_marketing_emails notification failed'
            )

    def has_website_permission(self, context):
        client_user = frappe.db.get_value('Customer', self.customer, 'linked_user')
        return frappe.session.user == client_user

    def get_context(self, context):
        context.title = self.player_name or 'Player Profile'
        context.parents = [{'title': 'My Players', 'route': '/dashboard'}]
        context.profile = self.as_dict()

    def on_update(self):
        try:
            mappings = [
                (
                    'owned_instruments',
                    'Instrument Profile',
                    {'player_profile': self.name},
                    ['name', 'serial_no', 'model'],
                    ['instrument', 'serial_no', 'model'],
                ),
                (
                    'setup_logs',
                    'Clarinet Setup Log',
                    {'player_profile': self.name},
                    ['name', 'setup_date'],
                    ['setup_log', 'setup_date'],
                ),
                (
                    'qa_findings',
                    'Clarinet Inspection',
                    {'player_profile': self.name},
                    ['name', 'status'],
                    ['inspection', 'status'],
                ),
                (
                    'repair_logs',
                    'Repair Log',
                    {'player_profile': self.name},
                    ['name', 'date', 'summary'],
                    ['repair_log', 'date', 'summary'],
                ),
                (
                    'tone_sessions',
                    'Intonation Session',
                    {'player_profile': self.name},
                    ['name', 'session_date'],
                    ['session', 'session_date'],
                ),
                (
                    'leak_tests',
                    'Leak Test',
                    {'player_profile': self.name},
                    ['name', 'test_date'],
                    ['test', 'test_date'],
                ),
                (
                    'wellness_scores',
                    'Instrument Wellness Score',
                    {'player_profile': self.name},
                    ['name', 'score'],
                    ['score_ref', 'score'],
                ),
            ]

            for table_field, doctype, filters, src_fields, tgt_fields in mappings:
                self.set(table_field, [])
                rows = frappe.get_all(doctype, filters=filters, fields=src_fields)
                for r in rows:
                    self.append(table_field, dict(zip(tgt_fields, [r[f] for f in src_fields])))
        except Exception:
            frappe.log_error(frappe.get_traceback(), 'PlayerProfile: on_update failed to sync logs')
