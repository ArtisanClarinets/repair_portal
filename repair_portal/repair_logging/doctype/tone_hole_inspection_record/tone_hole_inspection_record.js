// File Header
// Relative Path: repair_portal/repair_logging/doctype/tone_hole_inspection_record/tone_hole_inspection_record.js
// Last Updated: 2025-07-06
// Purpose: Client validations for Tone Hole Inspection Record

frappe.ui.form.on('Tone Hole Inspection Record', {
    validate(frm) {
        frm.doc.tone_hole_inspection.forEach(row => {
            if (!row.tone_hole_number) {
                frappe.throw(__('Each row must specify the Tone Hole Number.'));
            }
            if (!row.visual_status) {
                frappe.throw(__('Each row must specify Visual Status.'));
            }
            if (!row.photo) {
                frappe.throw(__('Each row must include a Photo.'));
            }
        });
    }
});
