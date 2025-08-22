# Relative Path: repair_portal/api/frontend/player_profile.py
# Last Updated: 2025-07-27
# Version: v1.1
# Purpose: Customer and staff Player Profile API for frontend
# Dependencies: Player Profile doctype, frappe.session

import frappe
from frappe import _
from frappe.utils import flt


def _as_bool(val):
    # Handles 0/1, '0'/'1', True/False
    return bool(int(val)) if isinstance(val, (int, str)) and str(val).isdigit() else bool(val)


def _listify(val):
    if not val:
        return []
    if isinstance(val, list):
        return val
    # Accepts comma- or newline-separated string
    if ',' in val:
        return [v.strip() for v in val.split(',') if v.strip()]
    if '\n' in val:
        return [v.strip() for v in val.split('\n') if v.strip()]
    return [val.strip()]


@frappe.whitelist(allow_guest=False)
def get():
    user = frappe.session.user
    roles = set(frappe.get_roles(user))
    staff_roles = {'Technician', 'Repair Manager', 'System Manager'}
    is_staff = bool(roles & staff_roles)
    email = frappe.db.get_value('User', user, 'email')
    profile_name = frappe.db.get_value('Player Profile', {'primary_email': email})
    if not profile_name:
        frappe.throw(_('No player profile linked to this user.'), frappe.PermissionError)
    doc = frappe.get_doc('Player Profile', profile_name)  # type: ignore

    def safe_table(doc, fieldname):
        value = getattr(doc, fieldname, [])
        return [row.as_dict() for row in (value or [])]

    out = {
        'player_profile_id': doc.name,
        'player_name': doc.player_name,  # type: ignore
        'preferred_name': doc.preferred_name,  # type: ignore
        'primary_email': doc.primary_email,  # type: ignore
        'primary_phone': doc.primary_phone,  # type: ignore
        'mailing_address': doc.mailing_address,  # type: ignore
        'profile_creation_date': doc.profile_creation_date,  # type: ignore
        'profile_status': doc.profile_status,  # type: ignore
        'player_level': doc.player_level,  # type: ignore
        'primary_playing_styles': _listify(doc.primary_playing_styles),  # type: ignore
        'affiliation': doc.affiliation,  # type: ignore
        'primary_teacher': doc.primary_teacher,  # type: ignore
        'key_height_preference': doc.key_height_preference,  # type: ignore
        'spring_tension_preference': doc.spring_tension_preference,  # type: ignore
        'preferred_pad_type': doc.preferred_pad_type,  # type: ignore
        'g_sharp_a_connection': doc.g_sharp_a_connection,  # type: ignore
        'intonation_notes': doc.intonation_notes,  # type: ignore
        'instruments_owned': safe_table(doc, 'instruments_owned'),
        'equipment_preferences': safe_table(doc, 'equipment_preferences'),
        'last_visit_date': doc.last_visit_date,  # type: ignore
        'customer_lifetime_value': flt(getattr(doc, 'customer_lifetime_value', 0)),
        'communication_preference': doc.communication_preference,  # type: ignore
        'newsletter_subscription': _as_bool(getattr(doc, 'newsletter_subscription', 0)),
        'targeted_marketing_optin': _listify(doc.targeted_marketing_optin),  # type: ignore
        'referral_source': doc.referral_source,  # type: ignore
        'is_staff': is_staff,
    }
    return out


@frappe.whitelist(allow_guest=False, methods=['POST'])
def save():
    import json

    user = frappe.session.user
    email = frappe.db.get_value('User', user, 'email')
    profile_name = frappe.db.get_value('Player Profile', {'primary_email': email})
    if not profile_name:
        frappe.throw(_('No player profile linked to this user.'), frappe.PermissionError)
    doc = frappe.get_doc('Player Profile', profile_name)  # type: ignore
    data = frappe.local.form_dict or json.loads(frappe.request.data or '{}')
    # Handle all editable fields
    for field in [
        'player_name',
        'preferred_name',
        'primary_email',
        'primary_phone',
        'mailing_address',
        'profile_creation_date',
        'profile_status',
        'player_level',
        'affiliation',
        'primary_teacher',
        'key_height_preference',
        'spring_tension_preference',
        'preferred_pad_type',
        'g_sharp_a_connection',
        'intonation_notes',
        'last_visit_date',
        'customer_lifetime_value',
        'communication_preference',
        'newsletter_subscription',
        'referral_source',
    ]:
        if field in data:
            setattr(doc, field, data[field])

    # Multiselects (accept list or string)
    if 'primary_playing_styles' in data:
        val = data['primary_playing_styles']
        if isinstance(val, list):
            doc.primary_playing_styles = ', '.join(val)  # type: ignore
        else:
            doc.primary_playing_styles = str(val)  # type: ignore
    if 'targeted_marketing_optin' in data:
        val = data['targeted_marketing_optin']
        if isinstance(val, list):
            doc.targeted_marketing_optin = ', '.join(val)  # type: ignore
        else:
            doc.targeted_marketing_optin = str(val)  # type: ignore

    # Booleans (newsletter_subscription)
    if 'newsletter_subscription' in data:
        doc.newsletter_subscription = int(bool(data['newsletter_subscription']))  # type: ignore

    # Child tables
    for table_field, table_doctype in [
        ('instruments_owned', 'Player Profile Instrument'),
        ('equipment_preferences', 'Player Profile Equipment'),
    ]:
        if table_field in data:
            doc.set(table_field, [])
            for row in data[table_field]:
                doc.append(table_field, row)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {'success': True}
