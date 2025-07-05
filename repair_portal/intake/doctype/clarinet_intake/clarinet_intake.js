frappe.ui.form.on('Clarinet Intake', {
  onload(frm) {
    if (!frm.doc.intake_type) {
      frm.set_value('intake_type', 'Inventory');
    }

    if (frm.doc.intake_type === 'Inventory') {
      if (!frm.doc.stock_status) {
        frm.set_value('stock_status', 'Inspection');
      }
      if (!frm.doc.inspected_by) {
        frm.set_value('inspected_by', frappe.session.user);
      }
    } else {
      if (!frm.doc.repair_status) {
        frm.set_value('repair_status', 'Pending');
      }
    }
  },

  refresh(frm) {
    if (!frm.doc.intake_type) {
      frm.set_value('intake_type', 'Inventory');
    }

    if (frm.doc.workflow_state) {
      frm.dashboard.add_indicator(
        __('Workflow: {0}', [frm.doc.workflow_state]),
        'blue'
      );
    }

    if (frm.doc.quality_inspection) {
      frm.add_custom_button(__('View Quality Inspection'), () => {
        frappe.set_route('Form', 'Quality Inspection', frm.doc.quality_inspection);
      });
    }
  },

  intake_type(frm) {
    const isRepair = frm.doc.intake_type === 'Repair';

    frm.set_df_property('purchase_order', 'reqd', !isRepair);
    frm.set_df_property('warehouse', 'reqd', !isRepair);
    frm.set_df_property('customer', 'reqd', isRepair);
    frm.set_df_property('due_date', 'reqd', isRepair);

    if (!isRepair) {
      if (!frm.doc.stock_status) {
        frm.set_value('stock_status', 'Inspection');
      }
      if (!frm.doc.inspected_by) {
        frm.set_value('inspected_by', frappe.session.user);
      }
    } else {
      if (!frm.doc.repair_status) {
        frm.set_value('repair_status', 'Pending');
      }
    }
  },

  validate(frm) {
    if (frm.doc.intake_type === 'Repair' && !frm.doc.customer) {
      frappe.throw(__('Customer is required for Repair intake type.'));
    }
  }
});
