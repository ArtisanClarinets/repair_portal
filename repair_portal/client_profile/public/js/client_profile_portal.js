// Enhances the Client Profile portal view with interactivity
frappe.ready(() => {
  if (frappe.web_form.doctype === "Client Profile") {
    frappe.web_form.after_load = () => {
      console.log("Client Profile Web Form loaded.");
    };

    frappe.web_form.on('preferred_contact_method', (field, value) => {
      frappe.show_alert(`Preferred contact method set to ${value}`);
    });
  }
});