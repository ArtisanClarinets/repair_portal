"""Display the pad map SVG for a given repair log."""

import frappe

frappe.only_for("Technician")


def get_context(context):
	"""Return context for /pad_map?name=<log>."""
	docname = frappe.form_dict.get("name")
	if not docname:
		frappe.throw("Missing repair log ID")

	repair_log = frappe.get_doc("Clarinet Repair Log", docname) # type: ignore
	svg_path = frappe.get_site_path(
		"public",
		"assets",
		"repair_portal",
		"images",
		"svg_pad_maps",
		"clarinet_upper_joint.svg",
	)

	try:
		with open(svg_path) as f:
			svg_content = f.read()
	except Exception:
		svg_content = "<!-- SVG not found -->"

	pad_data = [
		{
			"pad_id": pad.pad_id,
			"pad_name": pad.pad_name,
			"status": pad.status,
		}
		for pad in repair_log.pad_conditions # type: ignore
	]

	context.svg_content = svg_content
	context.pad_data = pad_data
	context.title = f"Pad Map for {repair_log.instrument}" # type: ignore
	return context
