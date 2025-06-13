// File: repair_portal/instrument_profile/page/instrument_history/instrument_history.js
frappe.pages['instrument_history'].on_page_load = function(wrapper) {
  let page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Instrument History',
    single_column: true
  });

  const instrument_id = frappe.get_route()[1];
  frappe.call({
    method: 'repair_portal.repair_portal.instrument_profile.page.instrument_history.instrument_history.get_instrument_history',
    args: { instrument_id },
    callback: function(r) {
      page.main.html(frappe.render_template("instrument_history", r.message));
    }
  });
};