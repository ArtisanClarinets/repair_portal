// File: repair_portal/public/js/client_portal/client_profile.js
// Last Updated: 2025-07-16
// Version: v1.0
// Purpose: Dynamic client profile rendering using AdminLTE layout

$(function() {
  const urlParams = new URLSearchParams(window.location.search);
  const clientId = urlParams.get('client_id');

  if (!clientId) {
    console.error("Missing client_id in URL");
    return;
  }

  frappe.call({
    method: 'repair_portal.api.get_client_profile',
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