frappe.ui.form.on('Player Profile', {
  refresh(frm) {
    // Show status badge
    if (frm.doc.profile_status) {
      frm.dashboard.clear_headline();
      frm.dashboard.set_headline(__('Profile Status: {0}', [frm.doc.profile_status]));
    }

    // Add Activate button if in Draft
    if (frm.doc.profile_status === 'Draft') {
      frm.add_custom_button(__('Activate'), () => {
        frappe.call({
          method: 'frappe.model.workflow.apply_workflow',
          args: {
            doc: frm.doc,
            action: 'Activate'
          },
          callback: () => {
            frm.reload_doc();
          }
        });
      }, __('Actions'));
    }

    // Add Archive button if Active
    if (frm.doc.profile_status === 'Active') {
      frm.add_custom_button(__('Archive'), () => {
        frappe.call({
          method: 'frappe.model.workflow.apply_workflow',
          args: {
            doc: frm.doc,
            action: 'Archive'
          },
          callback: () => {
            frm.reload_doc();
          }
        });
      }, __('Actions'));
    }
  }
});