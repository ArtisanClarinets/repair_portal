frappe.ui.form.on('Clarinet Intake', {
    onload(frm) {
        if (!frm.doc.intake_status) {
            frm.set_value('intake_status', 'Pending');
        }
    },
    refresh(frm) {
        // Hide item_code and inventory fields, show repair fields
        if (frm.doc.intake_type !== 'Inventory') {
            frm.set_df_property('item_code', 'hidden', 1);
            frm.set_df_property('item_code', 'reqd', 0);

            const show_fields = [
                'serial_no', 'customer_concerns', 'technician_remarks', 'customer_consent_form',
                'notes', 'instrument'
            ];
            show_fields.forEach(f => frm.set_df_property(f, 'hidden', 0));
            ['clarinet_initial_setup', 'brand', 'model', 'customer', 'instrument_type', 'date_purchased'].forEach(f => frm.set_df_property(f, 'hidden', 1));
        }
        // Modern intake status indicator
        if (frm.doc.intake_status) {
            let color = frm.doc.intake_status === "Pending" ? "orange"
                        : frm.doc.intake_status === "In Progress" ? "blue"
                        : frm.doc.intake_status === "Complete" ? "green" : "gray";
            frm.dashboard.clear_indicators && frm.dashboard.clear_indicators();
            frm.dashboard.add_indicator(frm.doc.intake_status, color);
        }
    },
    validate(frm) {
        let missing = [];
        if (!frm.doc.serial_no) missing.push("Serial Number");
        if (!frm.doc.customer_consent_form) missing.push("Consent/Liability Waiver (for Repair)");
        if (missing.length) {
            frappe.msgprint({
                title: "Missing Required Information",
                message: "Please fill the following fields:<br>" + missing.join("<br>"),
                indicator: "red"
            });
            frappe.validated = false;
        }
    },
    customer_consent_form(frm) {
        if (frm.doc.intake_type === "Repair" && !frm.doc.customer_consent_form) {
            frappe.show_alert({message: "Consent/Liability Waiver is required for Repair.", indicator: 'red'});
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
