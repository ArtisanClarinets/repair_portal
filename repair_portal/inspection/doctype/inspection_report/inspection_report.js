// File: repair_portal/inspection/doctype/inspection_report/inspection_report.js
// Updated: 2025-07-01
// Purpose: Custom client logic for Inspection Report. Adds Quick Launch QA/Repair, signature handling.

frappe.ui.form.on('Inspection Report', {
    refresh(frm) {
        // Quick Launch: New QA or Repair
        frm.add_custom_button('Quick QA', function() {
            frappe.new_doc('QA Report', {
                instrument_id: frm.doc.instrument_id,
                clarinet_intake_ref: frm.doc.clarinet_intake_ref,
            });
        }, __('Quick Launch'));

        frm.add_custom_button('Quick Repair', function() {
            frappe.new_doc('Repair Logging', {
                instrument_id: frm.doc.instrument_id,
                clarinet_intake_ref: frm.doc.clarinet_intake_ref,
            });
        }, __('Quick Launch'));

        // Show warning if flagged for reinspection
        if (frm.doc.flag_for_reinspection) {
            frm.dashboard.set_headline(__('This inspection is flagged for reinspection.'));
        }
    },
    validate(frm) {
        // Require digital signature if status is 'Passed' or 'Failed'
        if (["Passed", "Failed", "Pass", "Fail"].includes(frm.doc.status) && !frm.doc.digital_signature) {
            frappe.msgprint(__('Digital signature is required before completing the inspection.'));
        }
    }
});
