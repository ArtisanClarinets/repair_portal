frappe.ui.form.on('Clarinet Intake', {
    onload(frm) {
        // Default intake_status to 'Pending' if blank
        if (!frm.doc.intake_status) {
            frm.set_value('intake_status', 'Pending');
        }
    },
    refresh(frm) {
        // Show item_code and all inventory fields
        if (frm.doc.intake_type === 'Inventory') {
            frm.set_df_property('item_code', 'hidden', 0);
            frm.set_df_property('item_code', 'reqd', 1);

            const show_fields = [
                'serial_no', 'instrument_type', 'brand', 'model', 'customer',
                'date_purchased', 'notes', 'clarinet_initial_setup', 'instrument'
            ];
            show_fields.forEach(f => frm.set_df_property(f, 'hidden', 0));
            ['customer_concerns', 'technician_remarks', 'customer_consent_form'].forEach(f => frm.set_df_property(f, 'hidden', 1));
        }
        // Modern intake status indicator (using Frappe v15+ API)
        if (frm.doc.intake_status) {
            let color = frm.doc.intake_status === "Pending" ? "orange"
                        : frm.doc.intake_status === "In Progress" ? "blue"
                        : frm.doc.intake_status === "Complete" ? "green" : "gray";
            frm.dashboard.clear_indicators && frm.dashboard.clear_indicators();
            frm.dashboard.add_indicator(frm.doc.intake_status, color);
        }
    },
    intake_type(frm) {
        // Reset fields on type switch
        if (frm.doc.intake_type === 'Inventory') {
            frm.set_value('serial_no', '');
        }
    },
    validate(frm) {
        let missing = [];
        if (!frm.doc.serial_no) missing.push("Serial Number");
        if (!frm.doc.item_code) missing.push("Item Code");
        if (!frm.doc.instrument_type) missing.push("Instrument Type");
        if (!frm.doc.brand) missing.push("Brand");
        if (!frm.doc.model) missing.push("Model");
        if (!frm.doc.customer) missing.push("Client");
        if (!frm.doc.date_purchased) missing.push("Date Purchased");
        if (missing.length) {
            frappe.msgprint({
                title: "Missing Required Information",
                message: "Please fill the following fields:<br>" + missing.join("<br>"),
                indicator: "red"
            });
            frappe.validated = false;
        }
    },
    email(frm) {
        let email = frm.doc.customer_concerns || frm.doc.email;
        if (email && !/.+@.+\..+/.test(email)) {
            frappe.show_alert({message: "Please enter a valid email address.", indicator: 'orange'});
        }
    },
    phone(frm) {
        let phone = frm.doc.phone;
        if (phone && phone.replace(/\D/g, '').length < 10) {
            frappe.show_alert({message: "Please enter a valid phone number.", indicator: 'orange'});
        }
    }
});
