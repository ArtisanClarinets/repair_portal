frappe.ui.form.on('Instrument Profile', {
  refresh(frm) {
    if (frappe.user_roles.includes('System Manager')) {
      frm.add_custom_button('Renew Warranty', () => {
        frappe.prompt(
          [
            { fieldname: 'new_start_date', label: 'New Start Date', fieldtype: 'Date', reqd: 1 },
            { fieldname: 'new_end_date', label: 'New End Date', fieldtype: 'Date', reqd: 1 },
            { fieldname: 'reason', label: 'Reason for Renewal', fieldtype: 'Data', reqd: 1 },
          ],
          (values) => {
            frm.set_value('warranty_start_date', values.new_start_date);
            frm.set_value('warranty_end_date', values.new_end_date);
            frm.set_value('warranty_modification_reason', values.reason);
            frm.save();
          },
          'Renew Warranty'
        );
      });
    }

    frm.add_custom_button('View Lab Data', () => {
      frappe.set_route('lab-dashboard', { instrument: frm.doc.name });
    });
  },
});
