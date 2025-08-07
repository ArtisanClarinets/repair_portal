frappe.ui.form.on('Technician', {
    refresh: function(frm) {
        if (frm.doc.employment_status) {
            frm.dashboard.add_badge(frm.doc.employment_status, frm.doc.employment_status === "Active" ? "green" : frm.doc.employment_status === "Inactive" ? "orange" : "red");
        }
    },
    email: function(frm) {
        if (frm.doc.email && frm.doc.email.indexOf("@") === -1) {
            frappe.msgprint("Please enter a valid email address.");
        }
    },
    phone: function(frm) {
        if (frm.doc.phone && frm.doc.phone.replace(/\D/g, '').length < 10) {
            frappe.msgprint("Please enter a valid phone number.");
        }
    }
});
