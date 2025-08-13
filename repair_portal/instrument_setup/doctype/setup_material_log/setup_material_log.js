// File: repair_portal/repair_portal/instrument_setup/doctype/setup_material_log/setup_material_log.js
// Purpose: Client-side QoL for materials (server also computes amount)

frappe.ui.form.on('Setup Material Log', {
  item_code(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);
    if (!row.item_code) return;

    // Pull stock UOM + description for convenience
    frappe.db.get_value('Item', row.item_code, ['stock_uom', 'description'])
      .then(r => {
        if (!r || !r.message) return;
        const { stock_uom, description } = r.message;
        if (stock_uom && !row.uom) {
          frappe.model.set_value(cdt, cdn, 'uom', stock_uom);
        }
        if (description && !row.description) {
          frappe.model.set_value(cdt, cdn, 'description', description);
        }
      });
  },

  qty(frm, cdt, cdn) {
    recalc_amount(cdt, cdn);
  },

  rate(frm, cdt, cdn) {
    recalc_amount(cdt, cdn);
  }
});

function recalc_amount(cdt, cdn) {
  const row = frappe.get_doc(cdt, cdn);
  const qty = flt(row.qty || 0);
  const rate = flt(row.rate || 0);
  const amt = Math.round(qty * rate * 100) / 100.0;
  frappe.model.set_value(cdt, cdn, 'amount', amt);
}
