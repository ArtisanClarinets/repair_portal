/*  Client Profile form – UX sugar and state enforcement  */

frappe.ui.form.on("Client Profile", {
    refresh(frm) {
        decorate_status(frm);
        add_quick_buttons(frm);
        enforce_read_only(frm);
    },

    phone(frm) {
        const ok = !frm.doc.phone || /^\+?[0-9\-\s()]{7,20}$/.test(frm.doc.phone);
        if (!ok) {
            frappe.msgprint({
                title: __("Invalid phone"),
                message: __("Use digits, spaces, plus, dash or parentheses only."),
                indicator: "orange",
            });
        }
    },

    onload(frm) {
        if (!frm.doc.profile_status) {
            frm.set_value("profile_status", "Draft");
        }
    },

    before_save(frm) {
        if (frm.doc.phone && !/^\+?[0-9\-\s()]{7,20}$/.test(frm.doc.phone)) {
            frappe.throw(__("Please enter a valid phone number."));
        }
    },

    validate(frm) {
        if (!frm.doc.client_name) {
            frappe.throw(__("Client Name is required."));
        }
        if (!frm.doc.email) {
            frappe.throw(__("Email is required."));
        }
    },

    after_save(frm) {
        frappe.show_alert(__("Client Profile saved successfully."));
    },

    on_submit(frm) {
        frappe.show_alert(__("Client Profile submitted successfully."));
    }
});

// ---------- helpers ------------------------------------------------------

function decorate_status(frm) {
    const state = frm.doc.profile_status;
    const colors = {
        Draft: "orange",
        Active: "green",
        Approved: "blue",
        Archived: "gray",
        Deleted: "red"
    };
    if (!state) return;

    frm.dashboard.clear_headline();
    frm.dashboard.set_headline(__("Status: {0}", [state]), colors[state] || "blue");
    frm.dashboard.add_indicator(state, colors[state] || "blue");
}

function add_quick_buttons(frm) {
    if (frm.custom_buttons_added) return;
    frm.custom_buttons_added = true;

    if (frm.doc.profile_status === "Active") {
        frm.add_custom_button(
            __("New Repair Order"),
            () => frappe.new_doc("Repair Order", { client_profile: frm.doc.name }),
            __("Create")
        );
    }

    frm.add_custom_button(
        __("Sync Contact"),
        () => {
            frm.call("sync_contact").then(() => frappe.show_alert("Contact synced"));
        },
        __("Utilities")
    );
}

function enforce_read_only(frm) {
    const frozen_states = ["Archived", "Deleted"];
    if (frozen_states.includes(frm.doc.profile_status)) {
        frm.set_read_only();
        frappe.show_alert({
            message: `This Client Profile is <b>${frm.doc.profile_status}</b> and cannot be edited.`,
            indicator: 'orange'
        });
    }
}