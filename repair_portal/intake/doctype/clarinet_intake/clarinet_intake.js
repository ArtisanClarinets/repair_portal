// File: repair_portal/repair_portal/intake/doctype/clarinet_intake/clarinet_intake.js
// Updated: 2025-06-27
// Version: 1.1
// Purpose: Client script to update Inspection Completed field when inspection is submitted

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
                }
            });
        }
    }
});