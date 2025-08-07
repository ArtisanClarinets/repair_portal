// Consent Form JS Controller
frappe.ui.form.on('Consent Form', {
    consent_template: function(frm) {
        // Auto-populate field values based on required fields of template
        if (frm.doc.consent_template) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Consent Template',
                    name: frm.doc.consent_template
                },
                callback: function(r) {
                    if (r.message && r.message.required_fields) {
                        frm.clear_table('consent_field_values');
                        r.message.required_fields.forEach(function(field) {
                            var row = frm.add_child('consent_field_values');
                            row.field_label = field.field_label;
                            row.field_type = field.field_type;
                            frm.refresh_field('consent_field_values');
                        });
                    }
                }
            });
        }
    }
});
