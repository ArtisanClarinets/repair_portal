// -*- coding: utf-8 -*-
// Relative Path: repair_portal/repair/doctype/repair_actual_material/repair_actual_material.js
// Version: 1.1.0 (2025-09-17)
// Purpose:
//   Client UX for "Repair Actual Material":
//     - Backfill UOM when an Item is chosen (uses Item.stock_uom)
//     - Keep 'amount' visually in sync in the grid when qty or valuation_rate changes
// Notes:
//   Server remains source of truth; this improves grid UX.

frappe.ui.form.on("Repair Actual Material", {
  item_code(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row || !row.item_code) return;

    if (!row.uom) {
      frappe.db.get_value("Item", row.item_code, "stock_uom").then(({ message }) => {
        if (message && message.stock_uom) {
          frappe.model.set_value(cdt, cdn, "uom", message.stock_uom);
        }
      });
    }
  },

  qty: compute_amount,
  valuation_rate: compute_amount,
});

// --- helpers ---------------------------------------------------------------

function compute_amount(frm, cdt, cdn) {
  const row = locals[cdt][cdn];
  if (!row) return;

  const qty = flt(row.qty);
  const rate = flt(row.valuation_rate);
  const amount = qty * rate;

  // amount is read_only; we still set it so the grid shows the computed value immediately
  frappe.model.set_value(cdt, cdn, "amount", amount);
}

function flt(v) {
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}
