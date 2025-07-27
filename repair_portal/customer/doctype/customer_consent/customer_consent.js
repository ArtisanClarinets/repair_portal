frappe.ui.form.on('Customer Consent', {
    consent_template: function(frm) {
        // On selecting a consent template, fetch required fields and dynamically set up child table
        if(frm.doc.consent_template) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Consent Template',
                    name: frm.doc.consent_template
                },
                callback: function(r) {
                    if(r.message && r.message.required_fields) {
                        let req_fields = r.message.required_fields;
                        frm.clear_table('field_values');
                        req_fields.forEach(function(row) {
                            let child = frm.add_child('field_values');
                            child.field_label = row.field_label;
                        });
                        frm.refresh_field('field_values');
                    }
                }
            });
        }
    }
});
