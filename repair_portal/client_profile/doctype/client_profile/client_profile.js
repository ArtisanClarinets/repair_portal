/*  Client Profile form – ERPNext-native refactor */

frappe.ui.form.on("Client Profile", {
    refresh(frm) {
        decorate_status(frm);
        add_quick_buttons(frm);
        enforce_read_only(frm);
    },

    onload(frm) {
        if (!frm.doc.profile_status) {
            frm.set_value("profile_status", "Draft");
        }
    },

    validate(frm) {
        if (!frm.doc.customer) {
            frappe.throw(__("Customer link is required."));
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
            () => frappe.new_doc("Repair Order", { customer: frm.doc.customer }),
            __("Create")
        );
    }
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