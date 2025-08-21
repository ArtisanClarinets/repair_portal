# Relative Path: repair_portal/player_profile/portal/player_profile.py
# Last Updated: 2025-07-19
# Version: v1.1
# Purpose: Portal endpoint for Player Profile. Returns full profile context with session history, analytics, compliance flags, and audit logs for customer view.
# Dependencies: Frappe, Player Profile, Intonation Session, Instrument Profile, Instrument Inspection

import frappe
from frappe import _
from frappe.utils import getdate


def get_context(context):
	"""
	Portal page context for Player Profile. Exposes:
	- Profile details (no PII beyond allowed fields)
	- Linked instruments and recent service/QA logs
	- Session and repair analytics
	- Compliance status (e.g., age block)
	- Parental/guardian warning if under 13
	- All data validated for portal view security
	Args:
	    context: Standard Frappe web context dict
	Returns:
	    context dict for template rendering
	"""
	route = frappe.form_dict.route or frappe.request.path
	profile_name = route.split("/")[-1]
	profile = frappe.get_doc("Player Profile", profile_name)

	# Main profile fields
	allowed_fields = [
		"player_name",
		"profile_status",
		"pronouns",
		"date_of_birth",
		"school_year",
		"skill_level",
		"customer",
		"instrument_profiles",
		"owned_instruments",
		"setup_logs",
		"qa_findings",
		"repair_logs",
		"tone_sessions",
		"leak_tests",
		"wellness_scores",
	]
	context.profile = {f: getattr(profile, f, None) for f in allowed_fields}

	# Session analytics
	session_count = frappe.db.count("Intonation Session", {"player_profile": profile.name})
	last_session = frappe.db.get_value(
		"Intonation Session",
		{"player_profile": profile.name},
		"session_date",
		order_by="session_date desc",
	)
	repair_count = frappe.db.count("Repair Log", {"player_profile": profile.name})
	qa_pass_count = frappe.db.count(
		"Instrument Inspection", {"player_profile": profile.name, "status": "Pass"}
	)
	context.analytics = {
		"session_count": session_count,
		"last_session": last_session,
		"repair_count": repair_count,
		"qa_pass_count": qa_pass_count,
	}

	# Compliance flags
	dob = getattr(profile, "date_of_birth", None)
	context.compliance = {}
	if dob:
		age = (getdate(frappe.utils.nowdate()) - dob).days // 365
		context.compliance["age"] = age
		if age < 13:
			context.compliance["age_blocked"] = True
			context.compliance["warning"] = _("Marketing is blocked for this player due to age/compliance.")
	else:
		context.compliance["age_blocked"] = False

	# Parental user/email if blocked
	parent_user = frappe.db.get_value("Customer", profile.customer, "linked_user")
	parent_email = frappe.db.get_value("User", parent_user, "email") if parent_user else None
	if context.compliance.get("age_blocked") and parent_email:
		context.compliance["parent_email"] = parent_email

	# Only allow session user to see their own linked player
	if frappe.session.user != parent_user and frappe.session.user != profile.owner:
		frappe.throw(_("You do not have permission to view this player profile."))

	context.title = profile.player_name or "Player Profile"
	return context
