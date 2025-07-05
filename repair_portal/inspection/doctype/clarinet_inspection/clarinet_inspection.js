// File: repair_portal/intake/doctype/clarinet_inspection/clarinet_inspection.js
// Updated: 2025-07-03
// Version: 2.0
// Purpose: Production-grade script to mark Clarinet Intake inspection as completed when this inspection is submitted.

frappe.ui.form.on('Clarinet Inspection', {
    after_save(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.intake) {
            frappe.call({
                method: 'frappe.client.set_value',
                args: {
                    doctype: 'Clarinet Intake',
                    name: frm.doc.intake,
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
                        console.error('Error updating Clarinet Intake:', r.exc);
                    }
                },
                error: function(err) {
                    frappe.msgprint({
                        title: __('Server Error'),
                        message: __('An error occurred updating the linked Intake.'),
                        indicator: 'red'
                    });
                    console.error('Server error updating Clarinet Intake:', err);
                }
            });
        }
    }
});
