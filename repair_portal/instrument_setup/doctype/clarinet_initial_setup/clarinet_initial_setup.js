// File Header
// Relative Path: repair_portal/instrument_setup/doctype/clarinet_initial_setup/clarinet_initial_setup.js
// Last Updated: 2025-07-06
// Purpose: Client logic for Clarinet Initial Setup

frappe.ui.form.on('Clarinet Initial Setup', {
    refresh(frm) {
        if (frm.doc.status === 'Pass') {
            frm.dashboard.set_headline(__('Setup passed QA.'));
        } else if (frm.doc.status === 'Fail') {
            frm.dashboard.set_headline(__('Setup requires rework.'));
        }

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
    }
});
