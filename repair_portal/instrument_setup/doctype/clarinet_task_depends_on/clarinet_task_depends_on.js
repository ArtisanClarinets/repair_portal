// File: repair_portal/repair_portal/instrument_setup/doctype/clarinet_task_depends_on/clarinet_task_depends_on.js
// Purpose: Tiny UX sugar to open the dependency quickly.

frappe.ui.form.on('Clarinet Task Depends On', {
  task(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);
    if (row.task) {
      frappe.utils.copy_to_clipboard(row.task);
      frappe.show_alert({ message: __('Copied Task ID to clipboard.'), indicator: 'blue' });
    }
  }
});
