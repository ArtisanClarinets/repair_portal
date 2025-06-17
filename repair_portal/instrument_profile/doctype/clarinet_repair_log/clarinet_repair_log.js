// File: repair_portal/instrument_profile/doctype/clarinet_repair_log/clarinet_repair_log.js
// Updated: 2025-06-16
// Purpose: Add public pad map preview + resend email button

frappe.ui.form.on('Clarinet Repair Log', {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button('View Public Pad Map', () => {
        const url = `/pad-map?name=${frm.doc.name}`;
        window.open(url, '_blank');
      }, 'View');

      frm.add_custom_button('Resend Email to Customer', () => {
        frappe.call({
          method: 'repair_portal.instrument_profile.doctype.clarinet_repair_log.clarinet_repair_log.resend_email',
          args: { docname: frm.doc.name },
          callback: (r) => {
            frappe.msgprint('Email sent successfully');
          }
        });
      }, 'Actions');
    }
  }
});