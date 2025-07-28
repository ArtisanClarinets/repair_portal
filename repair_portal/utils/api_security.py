import frappe

def get_logged_in_user() -> str:
    """
    Returns the email/userid of the currently logged-in user.
    Raises an exception if not logged in.
    """
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("Not logged in", frappe.PermissionError)
    return user
