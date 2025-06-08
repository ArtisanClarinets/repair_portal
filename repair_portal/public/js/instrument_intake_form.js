// Client Script for Instrument Intake Form
frappe.ui.form.on('Instrument Intake Form', {
  customer: function(frm) {
    frappe.call({
      method: 'frappe.client.get_value',
      args: {
        doctype: 'Contact',
        filters: { 'customer': frm.doc.customer },
        fieldname: 'name'
      },
      callback: function(r) {
        if(r.message) {
          frm.set_value('contact_person', r.message.name);
        }
      }
    });
  }
});