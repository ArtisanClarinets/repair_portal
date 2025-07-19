// File: repair_portal/public/js/client_portal/customer.js
// Last Updated: 2025-07-16
// Version: v1.0
// Purpose: Dynamic client profile rendering using AdminLTE layout

$(function() {
  const urlParams = new URLSearchParams(window.location.search);
  const clientId = urlParams.get('client_id');

  if (!clientId) {
    frappe.msgprint({
      title: 'Missing Parameter',
      message: 'Client ID is required in URL parameters',
      indicator: 'red'
    });
    return;
  }

  frappe.call({
    method: 'repair_portal.api.get_customer',
    args: { client_id: clientId },
    callback: function(r) {
      if (r.message) {
        $('#client-name').text(r.message.full_name);
        $('#client-email').text(r.message.email);
        $('#repair-count').text(r.message.total_repairs);
      }
    }
  });
});