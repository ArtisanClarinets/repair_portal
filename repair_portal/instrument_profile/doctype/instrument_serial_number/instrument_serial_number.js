// File: repair_portal/.../instrument_serial/instrument_serial_number.js
// UX features:
//  - Quick create Clarinet Initial Setup
//  - Duplicate advisory
//  - Safe queries for Item when needed (inventory mapping optional)

frappe.ui.form.on("Instrument Serial", {
	refresh(frm) {
		add_actions(frm);
		advise_duplicates(frm);
	},

	ownership_type(frm) {
		toggle_owner_company_req(frm);
	},

	brand(frm) {
		advise_duplicates(frm);
	},
	serial_no(frm) {
		advise_duplicates(frm);
	},
	model(frm) {
		advise_duplicates(frm);
	},
	year_estimate(frm) {
		advise_duplicates(frm);
	},
});

function add_actions(frm) {
	if (frm.is_new()) return;
	if (frm.__actions_added) return;

	frm.add_custom_button(
		__("Create Clarinet Setup"),
		async () => {
			try {
				frappe.dom.freeze(__("Creating setup..."));
				const r = await frappe.call({ doc: frm.doc, method: "create_setup" });
				if (r && r.message && r.message.setup) {
					frm.set_value("current_setup", r.message.setup);
					await frm.save();
					frappe.set_route("Form", "Clarinet Initial Setup", r.message.setup);
				}
			} catch (e) {
				frappe.msgprint({
					message: __(e.message || "Failed to create setup."),
					indicator: "red",
				});
			} finally {
				frappe.dom.unfreeze();
			}
		},
		__("Actions"),
	);

	frm.__actions_added = true;
}

function advise_duplicates(frm) {
	if (frm.is_new()) return;
	frappe.debounce(async () => {
		try {
			const r = await frappe.call({ doc: frm.doc, method: "check_possible_duplicates" });
			const rows = (r && r.message) || [];
			if (rows.length) {
				const items = rows
					.map(
						(d) =>
							`${d.name} – ${d.brand || ""} ${d.model || ""} (${d.instrument_type || ""})`,
					)
					.join("<br>");
				frm.dashboard.set_headline(__("Possible duplicates detected."));
				frappe.show_alert({
					message: __("Duplicates:<br>{0}", [items]),
					indicator: "orange",
				});
			}
		} catch (e) {
			// silent
		}
	}, 800)();
}

function toggle_owner_company_req(frm) {
	// purely advisory; server enforces
	if (["Customer Owned", "Consignment"].includes(frm.doc.ownership_type)) {
		// encourage owner fields
	}
}
