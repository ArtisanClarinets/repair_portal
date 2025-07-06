// File Header
// Relative Path: repair_portal/repair_logging/doctype/tenon_fit_record/tenon_fit_record.js
// Last Updated: 2025-07-06
// Purpose: Client validations for Tenon Fit Record entries

frappe.ui.form.on('Tenon Fit Record', {
    validate(frm) {
        frm.doc.tenon_fit.forEach(row => {
            if (!row.joint) {
                frappe.throw(__('Each row must specify which joint is being measured.'));
            }
            if (!row.fit_classification) {
                frappe.throw(__('Each row must specify Fit Classification.'));
            }
            if (!row.notes && !row.measured_diameter) {
                frappe.throw(__('Each row must have either a Measured Diameter or Notes.'));
            }
        });
    }
});
