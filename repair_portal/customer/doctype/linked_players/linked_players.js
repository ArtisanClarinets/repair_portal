/**
 * File Header Template
 * Relative Path: repair_portal/customer/doctype/linked_players/linked_players.js
 * Last Updated: 2025-07-18
 * Version: v0.1
 * Purpose: Client‑side controller for the Linked Players child doctype.
 * Dependencies: Frappe framework, Player Profile doctype.
 */

frappe.ui.form.on("Linked Players", {
  /**
   * Triggered when a row in the Inline Grid is first rendered.
   * Adds sensible defaults to reduce user friction.
   */
  form_render: function (frm, cdt, cdn) {
    const row = locals[cdt][cdn];

    // Default relationship to "Self" if blank
    if (!row.relationship) {
      frappe.model.set_value(cdt, cdn, "relationship", "Self");
    }

    // Set today's date if blank
    if (!row.date_linked) {
      frappe.model.set_value(cdt, cdn, "date_linked", frappe.datetime.get_today());
    }
  },

  /**
   * Ensure only one Linked Player is marked as primary within the parent Customer.
   */
  is_primary: function (frm, cdt, cdn) {
    const current = locals[cdt][cdn];
    if (!current.is_primary) return;

    (frm.doc.linked_players || []).forEach(function (d) {
      if (d.name !== current.name && d.is_primary) {
        frappe.model.set_value(d.doctype, d.name, "is_primary", 0);
      }
    });

    frm.refresh_field("linked_players");
  },

  /**
   * Auto‑populate the Person field when a Player Profile is chosen,
   * improving data consistency and UX.
   */
  player_profile: function (frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row.player_profile || row.person) return;

    frappe.call({
      method: "frappe.client.get_value",
      args: {
        doctype: "Player Profile",
        filters: { name: row.player_profile },
        fieldname: "person",
      },
      freeze: true,
      freeze_message: __("Fetching linked Person…"),
      callback: function (r) {
        if (r.message) {
          frappe.model.set_value(cdt, cdn, "person", r.message.person);
        }
      },
    });
  },
});
