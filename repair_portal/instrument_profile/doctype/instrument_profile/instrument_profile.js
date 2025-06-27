frappe.ui.form.on('Instrument Profile', {
  refresh(frm) {
    if (frm.doc.profile_status === 'Waiting on Client') {
      frappe.msgprint(__('📌 Please link a valid Client Profile before progressing.'));
    }
    if (frm.doc.profile_status === 'Waiting on Player') {
      frappe.msgprint(__('🎯 Attach a Player Profile to continue setup.'));
    }
    if (frm.doc.profile_status === 'Ready for Use') {
      frappe.msgprint(__('✅ All profiles are in place. You may proceed to archive or deploy.'));
    }
  }
});