// -*- coding: utf-8 -*-
// Relative Path: repair_portal/repair/doctype/repair_planned_material/repair_planned_material.js
// Version: 1.1.0 (2025-09-17)
// Purpose:
//   Client UX for "Repair Planned Material":
//     - Backfill UOM from Item.stock_uom when Item selected
//     - Keep 'planned_amount' visually in sync in grid when qty or planned_rate changes
// Notes:
//   Server remains source of truth; this keeps the grid responsive.

frappe.ui.form.on("Repair Planned Material", {
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
  planned_rate: compute_amount,
});

// --- helpers ---------------------------------------------------------------

function compute_amount(frm, cdt, cdn) {
  const row = locals[cdt][cdn];
  if (!row) return;

  const qty = flt(row.qty);
  const rate = flt(row.planned_rate);
  const amount = qty * rate;

  // planned_amount is read_only; set it so users see the math immediately
  frappe.model.set_value(cdt, cdn, "planned_amount", amount);
}

function flt(v) {
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}
