// File Header
// Relative Path: repair_portal/inspection/doctype/initial_intake_inspection/initial_intake_inspection.js
// Last Updated: 2025-07-06
// Purpose: Client-side logic for Initial Intake Inspection (validations and UI enhancements)

frappe.ui.form.on('Initial Intake Inspection', {
    refresh(frm) {
        if (frm.doc.instrument_delivered) {
            frm.dashboard.set_headline(__('Instrument has been delivered to the customer.'));
        }

        if (frm.is_new()) {
            frm.set_value('inspection_date', frappe.datetime.get_today());
        }
    },
    validate(frm) {
        if (!frm.doc.digital_signature) {
            frappe.throw(__('Technician signature is required.'));
        }
        if (!frm.doc.rested_unopened) {
            frappe.throw(__('Instrument resting confirmation is required.'));
        }
        if (!frm.doc.tone_hole_inspection || frm.doc.tone_hole_inspection.length === 0) {
            frappe.throw(__('Please complete the tone hole inspection table.'));
        }
    }
});
