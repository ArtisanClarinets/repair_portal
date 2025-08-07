frappe.ui.form.on('Repair Order', {
  refresh(frm) {
    if (frm.doc.status === 'In Progress') {
      frm.add_custom_button(__('Start Timer'), () => {
        frappe.msgprint('Timer started for repair.');
      });
    }
  }
});