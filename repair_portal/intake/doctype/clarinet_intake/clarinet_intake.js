// Clarinet Intake client script (v2.0 — 2025-07-14)
frappe.ui.form.on("Clarinet Intake", {
  refresh(frm) {
    if (frm.doc.intake_type === "Inventory" && frm.doc.linked_initial_setup) {
      frm.add_custom_button(__('Open Initial Setup'), function() {
        frappe.set_route('Form', 'Clarinet Initial Setup', frm.doc.linked_initial_setup);
      }, __('Actions'));
    }
    // Remove any Repair Order buttons for Inventory
    if (frm.doc.intake_type === "Inventory") {
      frm.remove_custom_button(__('Open Repair Order'), __('Actions'));
    }
  }
});
