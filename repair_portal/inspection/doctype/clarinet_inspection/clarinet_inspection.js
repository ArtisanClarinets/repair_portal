// File: repair_portal/inspection/doctype/clarinet_inspection/clarinet_inspection.js
// Updated: 2025-07-05
// Purpose: Mark Clarinet Intake inspection as completed when this inspection is submitted. Now robust to missing linkage.

frappe.ui.form.on('Clarinet Inspection', {
    after_save(frm) {
        // Use the new robust clarinet_intake linkage
        if (frm.doc.docstatus === 1 && frm.doc.clarinet_intake) {
            frappe.call({
                method: 'frappe.client.set_value',
                args: {
                    doctype: 'Clarinet Intake',
                    name: frm.doc.clarinet_intake,
                    fieldname: 'inspection_completed',
                    value: 1
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.msgprint({
                            title: __('Inspection Marked Complete'),
                            message: __('Linked Clarinet Intake was updated successfully.'),
                            indicator: 'green'
                        });
                    } else {
                        frappe.msgprint({
                            title: __('Update Failed'),
                            message: __('Could not update Clarinet Intake.'),
                            indicator: 'red'
                        });
                        if (r.exc) {
                            frappe.log_error('Failed to update Clarinet Intake after Clarinet Inspection submit: ' + r.exc, frm.doc.name);
                        }
                    }
                },
                error: function(err) {
                    frappe.msgprint({
                        title: __('Server Error'),
                        message: __('An error occurred updating the linked Intake.'),
                        indicator: 'red'
                    });
                    frappe.log_error('Server error updating Clarinet Intake from Clarinet Inspection', JSON.stringify(err));
                }
            });
        } else if (frm.doc.docstatus === 1) {
            frappe.msgprint({
                title: __('Missing Intake Link'),
                message: __('This Clarinet Inspection is not linked to a Clarinet Intake. Please link before submitting.'),
                indicator: 'orange'
            });
            frappe.log_error('Clarinet Inspection submitted without clarinet_intake link', frm.doc.name);
        }
    }
});
