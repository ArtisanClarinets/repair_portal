// Path: repair_portal/customer/doctype/consent_form/consent_form.js
// Date: 2025-01-05
// Version: 3.0.0
// Description: Client-side form controller for Consent Form with signature, preview, and automation
// Dependencies: frappe, jQuery

frappe.ui.form.on('Consent Form', {
    setup(frm) {
        // Set query filters for proper linking
        frm.set_query('customer', () => ({
            filters: { disabled: 0 }
        }));

        frm.set_query('consent_template', () => ({
            filters: { disabled: 0, status: 'Active' }
        }));
    },

    onload(frm) {
        // Initialize signature canvas if not already loaded
        if (frm.doc.docstatus === 0 && !frm.doc.signature) {
            setup_signature_canvas(frm);
        }

        // Load required fields from template on first load
        if (frm.is_new() && frm.doc.consent_template) {
            refresh_required_fields(frm);
        }
    },

    refresh(frm) {
        // Clear any previous custom buttons
        frm.page.clear_actions_menu();
        frm.page.clear_primary_action();

        // Add custom buttons based on form state
        add_custom_buttons(frm);

        // Show signature field only if form is draft
        toggle_signature_field(frm);

        // Auto-render preview if content exists
        if (frm.doc.consent_template) {
            show_rendered_preview(frm);
        }

        // Validate signature requirements for submission
        validate_signature_requirements(frm);
    },

    consent_template(frm) {
        if (frm.doc.consent_template && frm.doc.docstatus === 0) {
            refresh_required_fields(frm);
        }
    },

    customer(frm) {
        if (frm.doc.customer && frm.doc.docstatus === 0) {
            // Auto-fill values when customer changes
            apply_auto_fill_values(frm);
        }
    },

    before_submit(frm) {
        // Final validation before submission
        if (!frm.doc.signature) {
            frappe.throw(__('Signature is required before submitting the consent form'));
        }

        // Confirm submission
        return new Promise((resolve, reject) => {
            frappe.confirm(
                __('Are you sure you want to submit this consent form? This action cannot be undone.'),
                () => resolve(),
                () => reject()
            );
        });
    }
});

// Child table events for consent field values
frappe.ui.form.on('Consent Field Value', {
    field_value(frm, cdt, cdn) {
        // Auto-update preview when field values change
        if (frm.doc.consent_template) {
            debounced_preview_update(frm);
        }
    }
});

// Helper functions

function add_custom_buttons(frm) {
    if (frm.doc.docstatus === 0) {
        // Draft state buttons
        frm.add_custom_button(__('Refresh from Template'), () => {
            refresh_from_template(frm);
        }, __('Actions'));

        frm.add_custom_button(__('Preview Content'), () => {
            show_preview_dialog(frm);
        }, __('Actions'));

        frm.add_custom_button(__('Auto-fill Fields'), () => {
            apply_auto_fill_values(frm);
        }, __('Actions'));

        if (frm.doc.signature) {
            frm.add_custom_button(__('Clear Signature'), () => {
                clear_signature(frm);
            }, __('Actions'));
        }

        // Primary action for getting signature
        if (!frm.doc.signature) {
            frm.page.set_primary_action(__('Add Signature'), () => {
                setup_signature_canvas(frm);
            });
        }
    } else if (frm.doc.docstatus === 1) {
        // Submitted state buttons
        frm.add_custom_button(__('View Rendered Content'), () => {
            show_preview_dialog(frm);
        });

        frm.add_custom_button(__('Download PDF'), () => {
            download_consent_pdf(frm);
        });
    }
}

function toggle_signature_field(frm) {
    // Show/hide signature field based on form state
    frm.toggle_display('signature', frm.doc.docstatus === 0);
    frm.toggle_display('signed_on', frm.doc.docstatus === 1);
}

function setup_signature_canvas(frm) {
    // Create signature dialog
    const dialog = new frappe.ui.Dialog({
        title: __('Add Signature'),
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'signature_canvas',
                label: __('Signature Canvas')
            }
        ],
        primary_action_label: __('Save Signature'),
        primary_action(values) {
            save_signature_data(frm, dialog);
        },
        secondary_action_label: __('Clear'),
        secondary_action() {
            clear_canvas();
        }
    });

    dialog.show();

    // Initialize canvas after dialog is shown
    dialog.$wrapper.find('.modal-body').append(`
        <div class="signature-pad-container" style="border: 1px solid #ccc; margin: 10px 0;">
            <canvas id="signature-pad" width="400" height="200" style="display: block;"></canvas>
        </div>
        <div class="signature-controls" style="text-align: center; margin: 10px 0;">
            <button type="button" class="btn btn-sm btn-default" onclick="clear_canvas()">
                ${__('Clear Canvas')}
            </button>
        </div>
    `);

    // Initialize signature pad (using basic canvas if signature_pad library not available)
    window.signature_canvas = document.getElementById('signature-pad');
    window.signature_context = window.signature_canvas.getContext('2d');
    window.is_drawing = false;

    // Mouse events
    window.signature_canvas.addEventListener('mousedown', start_drawing);
    window.signature_canvas.addEventListener('mousemove', draw);
    window.signature_canvas.addEventListener('mouseup', stop_drawing);

    // Touch events for mobile
    window.signature_canvas.addEventListener('touchstart', handle_touch);
    window.signature_canvas.addEventListener('touchmove', handle_touch);
    window.signature_canvas.addEventListener('touchend', stop_drawing);
}

function start_drawing(e) {
    window.is_drawing = true;
    const rect = window.signature_canvas.getBoundingClientRect();
    window.signature_context.beginPath();
    window.signature_context.moveTo(e.clientX - rect.left, e.clientY - rect.top);
}

function draw(e) {
    if (!window.is_drawing) return;
    const rect = window.signature_canvas.getBoundingClientRect();
    window.signature_context.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    window.signature_context.stroke();
}

function stop_drawing() {
    window.is_drawing = false;
    window.signature_context.beginPath();
}

function handle_touch(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouse_event = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 
                                     e.type === 'touchmove' ? 'mousemove' : 'mouseup', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    window.signature_canvas.dispatchEvent(mouse_event);
}

function clear_canvas() {
    if (window.signature_context) {
        window.signature_context.clearRect(0, 0, window.signature_canvas.width, window.signature_canvas.height);
    }
}

function save_signature_data(frm, dialog) {
    if (!window.signature_canvas) {
        frappe.msgprint(__('No signature canvas found'));
        return;
    }

    // Convert canvas to data URL
    const signature_data = window.signature_canvas.toDataURL('image/png');
    
    // Check if canvas is empty (basic check)
    const blank_canvas = document.createElement('canvas');
    blank_canvas.width = window.signature_canvas.width;
    blank_canvas.height = window.signature_canvas.height;
    
    if (signature_data === blank_canvas.toDataURL('image/png')) {
        frappe.msgprint(__('Please add a signature before saving'));
        return;
    }

    // Save to form
    frm.set_value('signature', signature_data);
    frm.set_value('signed_on', frappe.datetime.now_datetime());
    
    dialog.hide();
    frappe.show_alert({
        message: __('Signature saved successfully'),
        indicator: 'green'
    });
}

function clear_signature(frm) {
    frappe.confirm(
        __('Are you sure you want to clear the signature?'),
        () => {
            frm.set_value('signature', '');
            frm.set_value('signed_on', '');
        }
    );
}

function refresh_from_template(frm) {
    frappe.call({
        method: 'refresh_from_template',
        doc: frm.doc,
        callback: function(r) {
            if (r.message && r.message.status === 'success') {
                frm.reload_doc();
                frappe.show_alert({
                    message: r.message.message,
                    indicator: 'green'
                });
            }
        }
    });
}

function refresh_required_fields(frm) {
    if (!frm.doc.consent_template || frm.doc.docstatus !== 0) {
        return;
    }

    frappe.call({
        method: 'refresh_from_template',
        doc: frm.doc,
        callback: function(r) {
            if (r.message && r.message.status === 'success') {
                frm.refresh_field('consent_field_values');
                apply_auto_fill_values(frm);
            }
        }
    });
}

function apply_auto_fill_values(frm) {
    if (!frm.doc.customer || frm.doc.docstatus !== 0) {
        return;
    }

    // Trigger validation to apply auto-fill logic
    frm.script_manager.trigger('validate');
}

function show_rendered_preview(frm) {
    if (!frm.doc.consent_template) {
        return;
    }

    frappe.call({
        method: 'preview_render',
        doc: frm.doc,
        callback: function(r) {
            if (r.message) {
                // Show preview in a collapsible section
                const preview_html = `
                    <div class="consent-preview" style="margin: 15px 0;">
                        <div style="border: 1px solid #ddd; padding: 15px; background: #f9f9f9;">
                            <h5>${__('Rendered Preview')}</h5>
                            <div class="rendered-content">${r.message}</div>
                        </div>
                    </div>
                `;
                
                // Add to form if not already present
                if (!frm.fields_dict.preview_section) {
                    frm.add_custom_button(__('Toggle Preview'), () => {
                        $('.consent-preview').toggle();
                    });
                }
            }
        }
    });
}

function show_preview_dialog(frm) {
    frappe.call({
        method: 'preview_render',
        doc: frm.doc,
        callback: function(r) {
            if (r.message) {
                const dialog = new frappe.ui.Dialog({
                    title: __('Consent Form Preview'),
                    size: 'large',
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'preview_content',
                            options: `<div style="padding: 20px;">${r.message}</div>`
                        }
                    ]
                });
                dialog.show();
            }
        }
    });
}

function validate_signature_requirements(frm) {
    // Show warning if trying to submit without signature
    if (frm.doc.docstatus === 0 && !frm.doc.signature) {
        frm.dashboard.add_comment(__('Add a signature before submitting this form'), 'orange', true);
    }
}

function download_consent_pdf(frm) {
    if (frm.doc.docstatus !== 1) {
        frappe.msgprint(__('Form must be submitted to download PDF'));
        return;
    }

    // Generate PDF using Frappe's PDF generation
    const print_format = 'Standard'; // Use standard format or create custom
    const url = `/api/method/frappe.utils.print_format.download_pdf?doctype=${frm.doc.doctype}&name=${frm.doc.name}&format=${print_format}`;
    window.open(url, '_blank');
}

// Debounced preview update to avoid excessive API calls
let preview_timeout;
function debounced_preview_update(frm) {
    clearTimeout(preview_timeout);
    preview_timeout = setTimeout(() => {
        show_rendered_preview(frm);
    }, 1000);
}

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
