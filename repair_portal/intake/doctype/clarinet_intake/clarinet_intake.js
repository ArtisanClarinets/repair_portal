frappe.ui.form.on('Clarinet Intake', {
  refresh(frm) {
    if (!frm.doc.intake_type) {
      frm.set_value('intake_type', 'Inventory');
    }
  },

  intake_type(frm) {
    const isRepair = frm.doc.intake_type === 'Repair';
    frm.set_df_property('purchase_order', 'reqd', !isRepair);
    frm.set_df_property('warehouse', 'reqd', !isRepair);
    frm.set_df_property('customer', 'reqd', isRepair);
    frm.set_df_property('due_date', 'reqd', isRepair);
  },

  before_submit(frm) {
    if (frm.doc.intake_type === 'Inventory' && frm.doc.qc_status === 'Fail') {
      frappe.throw(__('Cannot submit: QC Failed.'));
    }
  },

  serial_number(frm) {
    if (frm.doc.serial_number) {
      frappe.call({
        method: 'repair_portal.intake.doctype.clarinet_intake.clarinet_intake.get_instrument_profile',
        args: { serial_number: frm.doc.serial_number },
        callback(r) {
          frm.set_value('instrument_profile', r.message || '');
        }
      });
    } else {
      frm.set_value('instrument_profile', '');
    }
  },

  instrument_profile(frm) {
    if (frm.doc.instrument_profile) {
      frappe.call({
        method: 'repair_portal.intake.doctype.clarinet_intake.clarinet_intake.get_instrument_details',
        args: { instrument_profile: frm.doc.instrument_profile },
        callback(r) {
          if (r.message) {
            frm.set_value('brand', r.message.brand || '');
            frm.set_value('model', r.message.model || '');
            frm.set_value('instrument_category', r.message.instrument_category || '');
          } else {
            frm.set_value('brand', '');
            frm.set_value('model', '');
            frm.set_value('instrument_category', '');
          }
        }
      });
    } else {
      frm.set_value('brand', '');
      frm.set_value('model', '');
      frm.set_value('instrument_category', '');
    }
  }
});
frappe.ui.form.on('Clarinet Intake', {
  onload(frm) {
    if (!frm.doc.serial_number) {
      frm.set_value('serial_number', '');
    }
  },

  validate(frm) {
    if (frm.doc.intake_type === 'Repair' && !frm.doc.customer) {
      frappe.throw(__('Customer is required for Repair intake type.'));
    }
  }
});