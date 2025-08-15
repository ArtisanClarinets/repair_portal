// Path: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.js
// Last Updated: 2025-08-14
// Version: v2.0
// Purpose: Client UX for Instrument Profile: status indicators and "Sync Now" action.

frappe.ui.form.on('Instrument Profile', {
  refresh(frm) {
    // Headline indicator
    if (frm.doc.status) {
      frm.dashboard.clear_headline();
      frm.dashboard.set_headline(__('Instrument Status: {0}', [frm.doc.status]));
    }

    // Warranty indicator
    if (frm.doc.warranty_end_date) {
      const days = frappe.datetime.get_diff(frm.doc.warranty_end_date, frappe.datetime.now_date());
      let color = 'green';
      if (days < 0) color = 'red';
      else if (days < 60) color = 'orange';
      frm.dashboard.add_indicator(
        __('Warranty Ends: {0}', [frappe.datetime.str_to_user(frm.doc.warranty_end_date)]),
        color
      );
    }

    // "Sync Now" action
    if (!frm.is_new()) {
      frm.add_custom_button(__('Sync Now'), () => {
        frm.dashboard.show_progress(__('Syncing…'), 20, 100);
        frappe.call({
          method: 'repair_portal.instrument_profile.services.profile_sync.sync_now',
          args: { profile: frm.doc.name },
        }).then(() => {
          frm.dashboard.show_progress(__('Syncing…'), 100, 100);
          frappe.show_alert({message: __('Profile synced'), indicator: 'green'});
          frm.reload_doc();
        }).catch(e => {
          frappe.msgprint({ title: __('Sync failed'), message: (e && e.message) || e, indicator: 'red' });
        });
      }).addClass('btn-primary');
    }
  }
});
