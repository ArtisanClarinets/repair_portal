// File Header
// Relative Path: repair_portal/inspection/doctype/intake_inspection/intake_inspection.js
// Last Updated: 2025-07-06
// Purpose: Client logic for Intake Inspection (Quick Launch, validations)

frappe.ui.form.on('Intake Inspection', {
    refresh(frm) {
        frm.add_custom_button('Quick QA', () => {
            frappe.new_doc('QA Report', {
                instrument_id: frm.doc.instrument_id,
                clarinet_intake_ref: frm.doc.clarinet_intake
            });
        }, __('Quick Launch'));

        frm.add_custom_button('Quick Repair', () => {
            frappe.new_doc('Repair Logging', {
                instrument_id: frm.doc.instrument_id,
                clarinet_intake_ref: frm.doc.clarinet_intake
            });
        }, __('Quick Launch'));

        if (frm.doc.flag_for_reinspection) {
            frm.dashboard.set_headline(__('This inspection is flagged for reinspection.'));
        }
    },
    validate(frm) {
        if (["Passed", "Failed", "Pass", "Fail"].includes(frm.doc.status) && !frm.doc.digital_signature) {
            frappe.throw(__('Digital signature required before completing inspection.'));
        }
    }
});
