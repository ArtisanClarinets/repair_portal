frappe.ui.form.on("Repair Request", {
	refresh: function (frm) {
		if (!frm.doc.__islocal && frm.doc.repair_status !== "Completed") {
			frm.add_custom_button(
				"Create Inspection",
				() => {
					frappe.new_doc("Repair Inspection", { repair_request: frm.doc.name });
				},
				"Create"
			);
		}

		// Status Color
		const status_color_map = {
			Pending: "orange",
			Inspected: "blue",
			Quoted: "purple",
			"In Progress": "green",
			"Awaiting Parts": "red",
			Completed: "green",
			Delivered: "grey",
		};
		if (frm.doc.repair_status && status_color_map[frm.doc.repair_status]) {
			frm.dashboard.set_headline(
				`<span style='color:${status_color_map[frm.doc.repair_status]}'>Status: ${
					frm.doc.repair_status
				}</span>`
			);
		}
	},

	contact: function (frm) {
		if (frm.doc.contact) {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Contact",
					name: frm.doc.contact,
				},
				callback: function (r) {
					if (r.message) {
						const contact = r.message;
						if (contact.email_id) frm.set_value("contact_email", contact.email_id);
						if (contact.phone) frm.set_value("contact_phone", contact.phone);
					}
				},
			});
		}
	},

	requested_services: function (frm) {
		let total = 0.0;
		(frm.doc.requested_services || []).forEach((service) => {
			if (service.estimated_price) total += service.estimated_price;
		});
		frm.set_df_property(
			"requested_services",
			"description",
			`Estimated Repair Cost: $${total.toFixed(2)}`
		);
	},
});
