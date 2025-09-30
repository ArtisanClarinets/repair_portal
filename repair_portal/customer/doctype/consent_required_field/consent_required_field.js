// Path: repair_portal/repair_portal/customer/doctype/consent_required_field/consent_required_field.js
// Date: 2025-01-27
// Version: 2.0.0
// Description: Client-side controller for Consent Required Field with auto-fieldname generation and validation
// Dependencies: frappe

frappe.ui.form.on('Consent Required Field', {
    field_label: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.field_label && !row.fieldname) {
            // Auto-generate fieldname from label
            const fieldname = frappe.scrub(row.field_label);
            frappe.model.set_value(cdt, cdn, 'fieldname', fieldname);
        }
    },
    
    field_type: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        // Show/hide options field based on field type
        if (row.field_type === 'Select' || row.field_type === 'Link') {
            frm.set_df_property('options', 'reqd', 1);
            frm.set_df_property('options', 'hidden', 0);
        } else {
            frm.set_df_property('options', 'reqd', 0);
            frm.set_df_property('options', 'hidden', 1);
            frappe.model.set_value(cdt, cdn, 'options', '');
        }
        
        // Set default validation based on field type
        if (row.field_type === 'Int' || row.field_type === 'Float') {
            if (!row.description) {
                const desc = row.field_type === 'Int' ? 
                    __('Enter a whole number') : 
                    __('Enter a decimal number');
                frappe.model.set_value(cdt, cdn, 'description', desc);
            }
        } else if (row.field_type === 'Date') {
            if (!row.description) {
                frappe.model.set_value(cdt, cdn, 'description', __('Select a date'));
            }
        } else if (row.field_type === 'Signature') {
            if (!row.description) {
                frappe.model.set_value(cdt, cdn, 'description', __('Digital signature required'));
            }
        }
    },
    
    options: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        // Validate Link DocType exists
        if (row.field_type === 'Link' && row.options) {
            frappe.db.exists('DocType', row.options).then(exists => {
                if (!exists) {
                    frappe.msgprint({
                        title: __('Invalid DocType'),
                        message: __('DocType {0} does not exist', [row.options]),
                        indicator: 'red'
                    });
                    frappe.model.set_value(cdt, cdn, 'options', '');
                }
            });
        }
        
        // Validate Select options format
        if (row.field_type === 'Select' && row.options) {
            const options = row.options.split('\n').filter(opt => opt.trim());
            if (options.length === 0) {
                frappe.msgprint({
                    title: __('Invalid Options'),
                    message: __('Select field must have at least one option'),
                    indicator: 'orange'
                });
            }
        }
    },
    
    required: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.required && !row.description) {
            frappe.model.set_value(cdt, cdn, 'description', __('This field is required'));
        }
    }
});

// Helper function to generate preview of field definition
frappe.ui.form.on('Consent Required Field', {
    before_save: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        
        // Generate fieldname if not provided
        if (row.field_label && !row.fieldname) {
            frappe.model.set_value(cdt, cdn, 'fieldname', frappe.scrub(row.field_label));
        }
        
        // Validate required combinations
        if ((row.field_type === 'Select' || row.field_type === 'Link') && !row.options) {
            frappe.validated = false;
            frappe.msgprint({
                title: __('Validation Error'),
                message: __('Options are required for {0} field type', [row.field_type]),
                indicator: 'red'
            });
        }
    }
});
