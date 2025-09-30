// Path: repair_portal/customer/doctype/consent_settings/consent_settings.js
// Date: 2025-09-30
// Version: 3.0.0
// Description: Client-side logic for Consent Settings - field management, validation, template creation
// Dependencies: frappe

frappe.ui.form.on('Consent Settings', {
    refresh(frm) {
        // Add custom buttons for automation
        frm.add_custom_button(__('Apply Linked Sources'), () => {
            frm.call('apply_linked_sources').then(r => {
                if (r.message) {
                    const result = r.message;
                    frappe.show_alert({
                        message: __('Applied {0} new fields, updated {1} fields, skipped {2} fields', 
                                   [result.created.length, result.updated.length, result.skipped.length]),
                        indicator: 'green'
                    });
                    if (result.skipped.length > 0) {
                        console.log('Skipped fields:', result.skipped);
                    }
                }
            });
        }, __('Actions'));

        frm.add_custom_button(__('Create Default Templates'), () => {
            frm.call('create_default_templates').then(r => {
                if (r.message && r.message.created_templates) {
                    frappe.show_alert({
                        message: __('Created {0} default templates', [r.message.count]),
                        indicator: 'green'
                    });
                } else {
                    frappe.show_alert({
                        message: __('Default templates already exist'),
                        indicator: 'blue'
                    });
                }
            });
        }, __('Actions'));

        frm.add_custom_button(__('Ensure Workflow'), () => {
            frm.call('ensure_workflow').then(r => {
                if (r.message) {
                    frappe.show_alert({
                        message: __('Workflow updated: {0}', [r.message.message || 'Success']),
                        indicator: 'green'
                    });
                }
            });
        }, __('Actions'));

        // Set up field queries
        _setup_field_queries(frm);
        
        // Refresh mapping and linked sources grids
        frm.refresh_field('mappings');
        frm.refresh_field('linked_sources');
    },

    validate(frm) {
        // Client-side validation before save
        return _validate_settings(frm);
    }
});

// Mappings child table events
frappe.ui.form.on('Consent Autofill Mapping', {
    source_doctype(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.source_doctype) {
            _update_fieldname_options(frm, row, 'source_fieldname');
        }
    },

    source_fieldname(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.source_doctype && row.source_fieldname) {
            _validate_field_mapping(row.source_doctype, row.source_fieldname);
        }
    },

    variable_name(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.variable_name) {
            // Validate snake_case format
            if (!/^[a-z][a-z0-9_]{2,}$/.test(row.variable_name)) {
                frappe.model.set_value(cdt, cdn, 'variable_name', '');
                frappe.msgprint(__('Variable name must be snake_case, start with letter, minimum 3 characters'));
            }
        }
    }
});

// Linked Sources child table events
frappe.ui.form.on('Consent Linked Source', {
    source_doctype(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.source_doctype && !row.label) {
            // Auto-suggest label
            frappe.model.set_value(cdt, cdn, 'label', row.source_doctype);
        }
    },

    fieldname(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.fieldname) {
            // Validate fieldname format
            if (!/^[a-z][a-z0-9_]{2,}$/.test(row.fieldname)) {
                frappe.model.set_value(cdt, cdn, 'fieldname', '');
                frappe.msgprint(__('Fieldname must be snake_case, start with letter, minimum 3 characters'));
            }
        }
    }
});

// Helper functions
function _setup_field_queries(frm) {
    // Query for source DocTypes (exclude child tables and custom)
    frm.set_query('source_doctype', 'mappings', () => ({
        filters: { 'is_child_table': 0, 'custom': 0 }
    }));

    frm.set_query('source_doctype', 'linked_sources', () => ({
        filters: { 'is_child_table': 0, 'custom': 0 }
    }));
}

function _update_fieldname_options(frm, row, fieldname) {
    if (!row.source_doctype) return;

    frappe.call({
        method: 'frappe.desk.form.meta.get_meta',
        args: { doctype: row.source_doctype },
        callback: (r) => {
            if (r.message && r.message.fields) {
                const options = r.message.fields
                    .filter(f => !f.hidden && f.fieldtype !== 'Table')
                    .map(f => f.fieldname);
                
                // You could use this to create an autocomplete or suggest fields
                console.log(`Available fields for ${row.source_doctype}:`, options);
            }
        }
    });
}

function _validate_field_mapping(source_doctype, source_fieldname) {
    frappe.call({
        method: 'repair_portal.customer.doctype.consent_settings.consent_settings.validate_field_mapping',
        args: {
            source_doctype: source_doctype,
            source_fieldname: source_fieldname
        },
        callback: (r) => {
            if (r.message && !r.message.valid) {
                frappe.show_alert({
                    message: __('Field mapping error: {0}', [r.message.error]),
                    indicator: 'red'
                });
            }
        }
    });
}

function _validate_settings(frm) {
    let valid = true;
    
    // Check for duplicate variable names in mappings
    const variable_names = (frm.doc.mappings || [])
        .map(m => m.variable_name)
        .filter(name => name);
    
    const unique_variables = [...new Set(variable_names)];
    if (variable_names.length !== unique_variables.length) {
        frappe.msgprint(__('Duplicate variable names found in mappings'));
        valid = false;
    }
    
    // Check for duplicate fieldnames in linked sources
    const fieldnames = (frm.doc.linked_sources || [])
        .map(s => s.fieldname)
        .filter(name => name);
    
    const unique_fieldnames = [...new Set(fieldnames)];
    if (fieldnames.length !== unique_fieldnames.length) {
        frappe.msgprint(__('Duplicate fieldnames found in linked sources'));
        valid = false;
    }
    
    return valid;
}

// Template validation helper
window.validate_consent_template = function(template_content) {
    if (!template_content) return;
    
    frappe.call({
        method: 'consent_settings.validate_template_syntax',
        doc: cur_frm.doc,
        args: { template_content: template_content },
        callback: (r) => {
            if (r.message) {
                const result = r.message;
                if (result.valid) {
                    frappe.show_alert({
                        message: __('Template syntax is valid'),
                        indicator: 'green'
                    });
                } else {
                    frappe.show_alert({
                        message: __('Template validation failed: {0}', [result.error || 'Unknown error']),
                        indicator: 'red'
                    });
                    
                    if (result.missing_variables && result.missing_variables.length > 0) {
                        frappe.msgprint({
                            title: __('Missing Variables'),
                            message: __('The following variables are not defined: {0}', 
                                       [result.missing_variables.join(', ')]),
                            indicator: 'orange'
                        });
                    }
                }
            }
        }
    });
};
