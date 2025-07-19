// File Header Template
// Relative Path: repair_portal/repair_logging/doctype/instrument_photo/instrument_photo.js
// Last Updated: 2025-07-17
// Version: v1.0
// Purpose: Client script for Instrument Photo, providing real-time validation, guidance, and UX polish for image documentation.
// Dependencies: frappe.ui.form

frappe.ui.form.on('Instrument Photo', {
  image(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row.label) {
      frappe.show_alert({
        message: __('Photo label is required—please describe the photo (e.g., Bell, Serial Number).'),
        indicator: 'orange'
      });
    }
  },
  label(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row.image) {
      frappe.show_alert({
        message: __('Please attach an image for this label.'),
        indicator: 'orange'
      });
    }
  },
  notes(frm, cdt, cdn) {
    // Optional: UX nudge if notes left empty
    const row = locals[cdt][cdn];
    if (!row.notes) {
      frappe.show_alert({
        message: __('Optional: Add notes for better documentation and QA.'),
        indicator: 'blue'
      });
    }
  }
});
