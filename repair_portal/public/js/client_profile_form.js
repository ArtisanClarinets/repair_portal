frappe.ready(function() {
  const form = document.querySelector('#client-profile-form');

  if (!form) return;

  form.addEventListener('submit', function(e) {
    e.preventDefault();

    const name = form.querySelector('[name="client_name"]');
    const email = form.querySelector('[name="client_email"]');
    if (!name.value.trim() || !email.value.trim()) {
      frappe.msgprint('Please complete all required fields.');
      return;
    }

    // Optional: implement Frappe AJAX form submission
    frappe.call({
      method: 'frappe.client.insert',
      args: {
        doc: {
          doctype: 'Client Profile',
          client_name: name.value,
          client_email: email.value
        }
      },
      callback: function(r) {
        if (!r.exc) {
          frappe.msgprint('Profile submitted successfully.');
          form.reset();
        }
      }
    });
  });
});