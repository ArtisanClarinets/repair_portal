import frappe


def get_context(context):
    user = frappe.session.user

    if user == 'Guest':
        frappe.throw('You must be logged in to view this page.')

    customer_name = frappe.db.get_value('Customer', {'linked_user': user})

    if not customer_name:
        return {'no_profile': True, 'title': 'My Customer'}

    profile = frappe.get_doc('Customer', customer_name)

    players = frappe.get_all(
        'Player Profile',
        filters={'customer': profile.name},
        fields=['name', 'player_name', 'route', 'published', 'profile_status'],
    )

    return {'profile': profile, 'players': players, 'title': 'My Customer'}
