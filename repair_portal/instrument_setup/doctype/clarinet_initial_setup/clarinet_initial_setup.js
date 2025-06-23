frappe.ui.form.on('Clarinet Initial Setup', {
  refresh: function(frm) {
    if (frm.doc.status === 'Pass') {
      frm.dashboard.set_headline(__('Setup passed QA.'));
    } else if (frm.doc.status === 'Fail') {
      frm.dashboard.set_headline(__('Setup requires rework.'));
    }
  },

  setup: function(frm) {
    frm.add_custom_button(__('Start Timer'), function() {
      frm.set_value('start_time', frappe.datetime.now_datetime());
    });
  }
});