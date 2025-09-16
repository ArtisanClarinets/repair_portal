// File: repair_portal/customer/doctype/consent_form/consent_form.js
// Version: v2.0.0 (2025-09-14)

frappe.ui.form.on('Consent Form', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button('Render Preview', () => {
                frappe.call({
                    method: 'repair_portal.repair_portal.customer.doctype.consent_form.consent_form.render_preview',
                    args: { name: frm.doc.name },
                    callback: (r) => {
                        if (r.message) {
                            frm.set_value('rendered_content', r.message);
                            frm.refresh_field('rendered_content');
                            frappe.show_alert({ message: 'Preview rendered.', indicator: 'green' });
                        }
                    }
                });
            });
        }
    },

    consent_template(frm) {
        if (!frm.doc.consent_template) { return; }
        // Pull required fields from the chosen template into child table
        frappe.call({
            method: 'frappe.client.get',
            args: { doctype: 'Consent Template', name: frm.doc.consent_template },
            callback(r) {
                if (r.message && r.message.required_fields) {
                    frm.clear_table('consent_field_values');
                    (r.message.required_fields || []).forEach((row) => {
                        let child = frm.add_child('consent_field_values');
                        child.field_label = row.field_label;
                        child.field_type = row.field_type;
                        child.field_value = row.default_value || '';
                    });
                    frm.refresh_field('consent_field_values');
                }
            }
        });
    }
});
