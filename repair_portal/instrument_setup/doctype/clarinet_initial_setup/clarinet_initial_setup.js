// File Header
// Relative Path: repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js
// Last Updated: 2025-07-17
// Purpose: Client logic for Clarinet Initial Setup, enhanced with work photo attachment, doc navigation, notifications, and real-time collaboration.

frappe.ui.form.on('Clarinet Initial Setup', {
    refresh(frm) {
        // QA dashboard
        if (frm.doc.status === 'Pass') {
            frm.dashboard.set_headline(__('Setup passed QA.'));
        } else if (frm.doc.status === 'Fail') {
            frm.dashboard.set_headline(__('Setup requires rework.'));
        }

        // Load Template Operations
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Load Template Operations'), () => {
                frappe.call({
                    method: "repair_portal.instrument_setup.doctype.clarinet_initial_setup.clarinet_initial_setup.load_operations_from_template",
                    args: {
                        docname: frm.doc.name
                    },
                    callback: (r) => {
                        if (!r.exc) {
                            frm.reload_doc();
                            frappe.msgprint(__('Default operations loaded from template.'));
                        }
                    }
                });
            });
        }

        // Attach Work Photos
        frm.add_custom_button(__('Attach Work Photos'), () => {
            new frappe.ui.FileUploader({
                allow_multiple: true,
                on_success(file) {
                    frappe.call({
                        method: 'frappe.client.attach_file',
                        args: {
                            doctype: frm.doctype,
                            docname: frm.doc.name,
                            file_url: file.file_url
                        },
                        callback: () => frm.reload_doc()
                    });
                }
            });
        });

        // View Instrument Profile if linked
        if (frm.doc.instrument_profile) {
            frm.add_custom_button(__('View Instrument Profile'), () => {
                frappe.set_route('Form', 'Instrument Profile', frm.doc.instrument_profile);
            });
        }

        // View Job Card or Maintenance Visit if linked
        if (frm.doc.job_card) {
            frm.add_custom_button(__('View Job Card'), () => {
                frappe.set_route('Form', 'Job Card', frm.doc.job_card);
            });
        }
        if (frm.doc.maintenance_visit) {
            frm.add_custom_button(__('View Maintenance Visit'), () => {
                frappe.set_route('Form', 'Maintenance Visit', frm.doc.maintenance_visit);
            });
        }

        // WebSocket real-time updates (doc sync)
        if (frappe.socketio) {
            frappe.realtime.on('doc_update', function(data) {
                if (data.doctype === frm.doctype && data.name === frm.doc.name) {
                    frappe.show_alert({ message: __('This setup was updated by another user.'), indicator: 'blue' });
                    frm.reload_doc();
                }
            });
        }
    },
    setup(frm) {
        frm.add_custom_button(__('Start Timer'), function() {
            frm.set_value('start_time', frappe.datetime.now_datetime());
        });
    },
    validate(frm) {
        if (frm.doc.operations_performed && frm.doc.operations_performed.length > 0) {
            const incomplete = frm.doc.operations_performed.some(row => !row.completed);
            if (incomplete) {
                frappe.throw(__('All Setup Operations must be completed before submission.'));
            }
        }
    },
    after_save(frm) {
        // Customer notification on QA pass and submit
        if (frm.doc.status === 'Pass' && frm.doc.docstatus === 1) {
            frappe.call({
                method: 'repair_portal.instrument_setup.doctype.clarinet_initial_setup.clarinet_initial_setup.notify_customer_on_completion',
                args: { docname: frm.doc.name },
                freeze: true
            });
        }
    }
});
