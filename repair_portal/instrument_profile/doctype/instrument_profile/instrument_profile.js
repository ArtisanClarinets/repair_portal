// File Header Template
// Relative Path: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.js
// Last Updated: 2025-07-17
// Version: v1.2
// Purpose: Instrument Profile client logic for dashboards, status, workflow actions, and warranty expiration UX
// Dependencies: frappe.ui.form, frappe.model.workflow

frappe.ui.form.on('Instrument Profile', {
  refresh(frm) {
    // Show status badges
    if (frm.doc.status) {
      frm.dashboard.clear_headline();
      frm.dashboard.set_headline(__('Instrument Status: {0}', [frm.doc.status]));
    }

    // Show buttons for manual actions if permitted
    if (frm.doc.status === 'Awaiting Pickup') {
      frm.add_custom_button(__('Deliver Instrument'), () => {
        frappe.call({
          method: 'frappe.model.workflow.apply_workflow',
          args: {
            doc: frm.doc,
            action: 'Deliver'
          },
          callback: () => {
            frm.reload_doc();
          }
        });
      }, __('Actions'));
    }

    if (frm.doc.status === 'Delivered') {
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

    // Add verification status indicator
    if (frm.doc.verification_status) {
      frm.dashboard.add_indicator(
        __('Verification: {0}', [frm.doc.verification_status]),
        {
          'Pending': 'orange',
          'Approved': 'green',
          'Rejected': 'red'
        }[frm.doc.verification_status] || 'gray'
      );
    }

    // Add workflow state indicator
    if (frm.doc.workflow_state) {
      frm.dashboard.add_indicator(
        __('Workflow: {0}', [frm.doc.workflow_state]),
        'blue'
      );
    }

    // Warranty expiration dashboard indicator
    if (frm.doc.warranty_expiration) {
      const days = frappe.datetime.get_diff(frm.doc.warranty_expiration, frappe.datetime.now_date());
      let color = 'green';
      if (days < 0) color = 'red';
      else if (days < 60) color = 'orange';
      frm.dashboard.add_indicator(
        __('Warranty: {0}', [frappe.datetime.str_to_user(frm.doc.warranty_expiration)]),
        color
      );
    }
  }
});
