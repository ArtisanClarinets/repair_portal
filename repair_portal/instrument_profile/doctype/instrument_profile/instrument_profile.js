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
  }
});