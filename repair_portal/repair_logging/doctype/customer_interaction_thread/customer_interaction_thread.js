// Path: repair_logging/doctype/customer_interaction_thread/customer_interaction_thread.js
// Enhances form UI for message grouping and thread context

frappe.ui.form.on('Customer Interaction Thread', {
	refresh(frm) {
		frm.set_df_property('message', 'reqd', 1);
		frm.set_df_property('channel', 'reqd', 1);
	}
});