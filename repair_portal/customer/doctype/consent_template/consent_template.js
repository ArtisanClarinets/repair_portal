// Path: repair_portal/customer/doctype/consent_template/consent_template.js
// Date: 2025-01-05
// Version: 3.0.0
// Description: Client-side form controller for Consent Template with Jinja validation and preview
// Dependencies: frappe, CodeMirror (optional)

frappe.ui.form.on('Consent Template', {
    setup(frm) {
        // Set field properties
        setup_field_properties(frm);
    },

    onload(frm) {
        // Initialize template editor
        setup_template_editor(frm);
        
        // Load usage statistics if not new
        if (!frm.is_new()) {
            load_usage_statistics(frm);
        }
    },

    refresh(frm) {
        // Clear previous custom buttons
        frm.page.clear_actions_menu();
        
        // Add custom buttons based on form state
        add_custom_buttons(frm);
        
        // Show usage statistics
        if (!frm.is_new()) {
            show_usage_info(frm);
        }
        
        // Validate template on load
        if (frm.doc.template_content) {
            validate_template_syntax(frm);
        }
    },

    template_content(frm) {
        // Debounced validation when content changes
        debounced_template_validation(frm);
    },

    template_name(frm) {
        // Update title display
        if (frm.doc.template_name) {
            frm.page.set_title(frm.doc.template_name);
        }
    },

    disabled(frm) {
        // Update status when disabled flag changes
        if (frm.doc.disabled) {
            frm.set_value('status', 'Inactive');
        } else {
            frm.set_value('status', 'Active');
        }
    }
});

// Child table events for required fields
frappe.ui.form.on('Consent Required Field', {
    field_name(frm, cdt, cdn) {
        // Auto-generate field label from field name
        const row = locals[cdt][cdn];
        if (row.field_name && !row.field_label) {
            frappe.model.set_value(cdt, cdn, 'field_label', 
                frappe.model.unscrub(row.field_name));
        }
        
        // Validate field name format
        validate_field_name(frm, cdt, cdn);
    },

    field_label(frm, cdt, cdn) {
        // Auto-generate field name from field label
        const row = locals[cdt][cdn];
        if (row.field_label && !row.field_name) {
            frappe.model.set_value(cdt, cdn, 'field_name', 
                frappe.scrub(row.field_label));
        }
        
        // Check for duplicates
        check_duplicate_labels(frm);
    },

    field_type(frm, cdt, cdn) {
        // Update default value field based on type
        setup_default_value_field(frm, cdt, cdn);
    }
});

// Helper functions

function setup_field_properties(frm) {
    // Make template content a code editor
    frm.set_df_property('template_content', 'options', 'HTML');
    
    // Set field descriptions
    frm.set_df_property('template_content', 'description', 
        __('Use Jinja2 template syntax. Available variables: {{ customer_name }}, {{ date }}, {{ form }}, and field variables.'));
}

function setup_template_editor(frm) {
    // Enhanced editor for template content if CodeMirror is available
    if (frm.fields_dict.template_content && window.CodeMirror) {
        const field = frm.fields_dict.template_content;
        if (field.$input && !field.editor) {
            field.editor = CodeMirror.fromTextArea(field.$input.get(0), {
                mode: 'htmlmixed',
                lineNumbers: true,
                theme: 'default',
                lineWrapping: true,
                autoCloseTags: true,
                matchBrackets: true
            });
            
            // Update field value when editor changes
            field.editor.on('change', function() {
                const content = field.editor.getValue();
                frm.set_value('template_content', content);
            });
        }
    }
}

function add_custom_buttons(frm) {
    if (frm.doc.docstatus === 0) {
        // Draft state buttons
        frm.add_custom_button(__('Validate Template'), () => {
            validate_template_syntax(frm, true);
        }, __('Template'));

        frm.add_custom_button(__('Preview with Sample Data'), () => {
            show_preview_dialog(frm);
        }, __('Template'));

        frm.add_custom_button(__('Get Available Variables'), () => {
            show_variables_dialog(frm);
        }, __('Template'));

        if (frm.doc.template_content) {
            frm.add_custom_button(__('Test Render'), () => {
                test_template_render(frm);
            }, __('Template'));
        }

        // Actions menu
        frm.add_custom_button(__('Duplicate Template'), () => {
            duplicate_template_dialog(frm);
        }, __('Actions'));
    }

    if (!frm.is_new()) {
        frm.add_custom_button(__('Usage Statistics'), () => {
            show_usage_statistics_dialog(frm);
        }, __('View'));
        
        frm.add_custom_button(__('Related Forms'), () => {
            show_related_forms(frm);
        }, __('View'));
    }
}

function validate_template_syntax(frm, show_message = false) {
    if (!frm.doc.template_content) {
        if (show_message) {
            frappe.msgprint(__('No template content to validate'));
        }
        return;
    }

    frappe.call({
        method: 'validate_template_syntax',
        doc: frm.doc,
        callback: function(r) {
            if (r.message) {
                const result = r.message;
                if (result.valid) {
                    if (show_message) {
                        frappe.show_alert({
                            message: __('Template syntax is valid'),
                            indicator: 'green'
                        });
                    }
                    // Remove any previous error indicators
                    remove_field_error(frm, 'template_content');
                } else {
                    // Show error
                    show_field_error(frm, 'template_content', result.message);
                    if (show_message) {
                        frappe.msgprint({
                            title: __('Template Validation Failed'),
                            message: result.message,
                            indicator: 'red'
                        });
                    }
                }
            }
        }
    });
}

function show_preview_dialog(frm) {
    frappe.call({
        method: 'preview_with_sample_data',
        doc: frm.doc,
        callback: function(r) {
            if (r.message) {
                const dialog = new frappe.ui.Dialog({
                    title: __('Template Preview'),
                    size: 'large',
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'preview_content',
                            options: `<div style="padding: 20px; border: 1px solid #ddd; background: white;">${r.message}</div>`
                        }
                    ]
                });
                dialog.show();
            }
        }
    });
}

function show_variables_dialog(frm) {
    frappe.call({
        method: 'get_available_variables',
        doc: frm.doc,
        callback: function(r) {
            if (r.message) {
                const variables = r.message;
                const variable_list = variables.map(v => `<li><code>{{ ${v} }}</code></li>`).join('');
                
                const dialog = new frappe.ui.Dialog({
                    title: __('Available Template Variables'),
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'variables_list',
                            options: `
                                <div style="padding: 15px;">
                                    <h5>${__('Available Variables:')}</h5>
                                    <ul style="list-style-type: none; padding-left: 0;">
                                        ${variable_list}
                                    </ul>
                                    <p><small>${__('Use these variables in your template content with double curly braces.')}</small></p>
                                </div>
                            `
                        }
                    ]
                });
                dialog.show();
            }
        }
    });
}

function test_template_render(frm) {
    // Quick syntax test
    frappe.call({
        method: 'repair_portal.customer.doctype.consent_template.consent_template.validate_template_content',
        args: {
            content: frm.doc.template_content
        },
        callback: function(r) {
            if (r.message) {
                const result = r.message;
                frappe.msgprint({
                    title: __('Template Test Result'),
                    message: result.message,
                    indicator: result.valid ? 'green' : 'red'
                });
            }
        }
    });
}

function duplicate_template_dialog(frm) {
    const dialog = new frappe.ui.Dialog({
        title: __('Duplicate Template'),
        fields: [
            {
                fieldtype: 'Data',
                fieldname: 'new_name',
                label: __('New Template Name'),
                reqd: 1
            }
        ],
        primary_action_label: __('Create Duplicate'),
        primary_action(values) {
            frappe.call({
                method: 'duplicate_template',
                doc: frm.doc,
                args: {
                    new_name: values.new_name
                },
                callback: function(r) {
                    if (r.message) {
                        dialog.hide();
                        frappe.show_alert({
                            message: __('Template duplicated successfully'),
                            indicator: 'green'
                        });
                        // Navigate to new template
                        frappe.set_route('Form', 'Consent Template', r.message);
                    }
                }
            });
        }
    });
    dialog.show();
}

function load_usage_statistics(frm) {
    frappe.call({
        method: 'get_usage_statistics',
        doc: frm.doc,
        callback: function(r) {
            if (r.message) {
                frm.usage_stats = r.message;
                show_usage_info(frm);
            }
        }
    });
}

function show_usage_info(frm) {
    if (!frm.usage_stats) return;
    
    const stats = frm.usage_stats;
    const usage_html = `
        <div class="usage-info" style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px;">
            <h5>${__('Template Usage')}</h5>
            <div class="row">
                <div class="col-sm-4">
                    <div class="text-center">
                        <div style="font-size: 24px; font-weight: bold; color: #5e64ff;">${stats.total_forms}</div>
                        <div style="font-size: 12px; color: #8d99ae;">${__('Total Forms')}</div>
                    </div>
                </div>
                <div class="col-sm-4">
                    <div class="text-center">
                        <div style="font-size: 24px; font-weight: bold; color: #ff6b6b;">${stats.active_forms}</div>
                        <div style="font-size: 12px; color: #8d99ae;">${__('Active Forms')}</div>
                    </div>
                </div>
                <div class="col-sm-4">
                    <div class="text-center">
                        <div style="font-size: 24px; font-weight: bold; color: #51cf66;">${stats.submitted_forms}</div>
                        <div style="font-size: 12px; color: #8d99ae;">${__('Submitted Forms')}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add to form sidebar or create custom section
    if (frm.sidebar && frm.sidebar.find('.usage-info').length === 0) {
        frm.sidebar.append(usage_html);
    }
}

function show_usage_statistics_dialog(frm) {
    if (!frm.usage_stats) {
        load_usage_statistics(frm);
        return;
    }
    
    const stats = frm.usage_stats;
    const recent_forms_html = stats.recent_forms.map(form => 
        `<tr>
            <td><a href="/app/consent-form/${form.name}">${form.name}</a></td>
            <td>${form.customer || ''}</td>
            <td>${form.status || ''}</td>
            <td>${frappe.datetime.str_to_user(form.creation)}</td>
        </tr>`
    ).join('');
    
    const dialog = new frappe.ui.Dialog({
        title: __('Template Usage Statistics'),
        size: 'large',
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'stats_content',
                options: `
                    <div style="padding: 20px;">
                        <div class="row text-center" style="margin-bottom: 30px;">
                            <div class="col-sm-4">
                                <div style="padding: 20px; background: #f1f3f4; border-radius: 8px;">
                                    <h3 style="color: #5e64ff; margin: 0;">${stats.total_forms}</h3>
                                    <p style="margin: 5px 0 0 0;">${__('Total Forms')}</p>
                                </div>
                            </div>
                            <div class="col-sm-4">
                                <div style="padding: 20px; background: #f1f3f4; border-radius: 8px;">
                                    <h3 style="color: #ff6b6b; margin: 0;">${stats.active_forms}</h3>
                                    <p style="margin: 5px 0 0 0;">${__('Active Forms')}</p>
                                </div>
                            </div>
                            <div class="col-sm-4">
                                <div style="padding: 20px; background: #f1f3f4; border-radius: 8px;">
                                    <h3 style="color: #51cf66; margin: 0;">${stats.submitted_forms}</h3>
                                    <p style="margin: 5px 0 0 0;">${__('Submitted Forms')}</p>
                                </div>
                            </div>
                        </div>
                        
                        <h4>${__('Recent Forms')}</h4>
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>${__('Form ID')}</th>
                                    <th>${__('Customer')}</th>
                                    <th>${__('Status')}</th>
                                    <th>${__('Created')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${recent_forms_html || '<tr><td colspan="4" class="text-center">' + __('No forms found') + '</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                `
            }
        ]
    });
    dialog.show();
}

function show_related_forms(frm) {
    frappe.route_options = {
        'consent_template': frm.doc.name
    };
    frappe.set_route('List', 'Consent Form');
}

function validate_field_name(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (row.field_name) {
        // Check if field name is valid (alphanumeric and underscores only)
        const valid_pattern = /^[a-zA-Z_][a-zA-Z0-9_]*$/;
        if (!valid_pattern.test(row.field_name)) {
            frappe.msgprint(__('Field name must start with a letter or underscore and contain only letters, numbers, and underscores'));
            frappe.model.set_value(cdt, cdn, 'field_name', '');
        }
    }
}

function check_duplicate_labels(frm) {
    const labels = [];
    const duplicates = [];
    
    (frm.doc.required_fields || []).forEach(row => {
        if (row.field_label) {
            const label_lower = row.field_label.toLowerCase();
            if (labels.includes(label_lower)) {
                if (!duplicates.includes(label_lower)) {
                    duplicates.push(label_lower);
                }
            } else {
                labels.push(label_lower);
            }
        }
    });
    
    if (duplicates.length > 0) {
        frappe.msgprint(__('Duplicate field labels detected: {0}', [duplicates.join(', ')]));
    }
}

function setup_default_value_field(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    // Could enhance this to change field type of default_value based on field_type
    // For now, keep as simple text field
}

function show_field_error(frm, fieldname, message) {
    const field = frm.fields_dict[fieldname];
    if (field) {
        field.$wrapper.addClass('has-error');
        if (!field.$wrapper.find('.error-message').length) {
            field.$wrapper.append(`<div class="error-message text-danger" style="margin-top: 5px;">${message}</div>`);
        }
    }
}

function remove_field_error(frm, fieldname) {
    const field = frm.fields_dict[fieldname];
    if (field) {
        field.$wrapper.removeClass('has-error');
        field.$wrapper.find('.error-message').remove();
    }
}

// Debounced template validation to avoid excessive API calls
let validation_timeout;
function debounced_template_validation(frm) {
    clearTimeout(validation_timeout);
    validation_timeout = setTimeout(() => {
        validate_template_syntax(frm);
    }, 1500);
}
