// Prototype client logic (Frappe v15)

frappe.ui.form.on('Prototype', {
  refresh(frm) {
    // Button: Open Designer
    frm.add_custom_button('Open Designer', () => {
      frappe.call({
        method: 'repair_portal.prototyping.doctype.prototype.prototype.open_designer_url',
        args: { prototype: frm.doc.name }
      }).then(r => {
        if (r.message) window.location.href = r.message;
      });
    }, __('Actions'));

    // Button: Create Item & BOM
    frm.add_custom_button('Create Item & BOM', () => {
      frappe.call({
        method: 'repair_portal.prototyping.doctype.prototype.prototype.make_item_and_bom',
        args: { prototype: frm.doc.name }
      }).then(r => {
        frappe.show_alert({message: __('Item/BOM created.'), indicator: 'green'});
        frm.reload_doc();
      });
    }, __('Actions'));

    // Button: Create Work Order
    frm.add_custom_button('Create Work Order', () => {
      frappe.call({
        method: 'repair_portal.prototyping.doctype.prototype.prototype.make_work_order',
        args: { prototype: frm.doc.name }
      }).then(r => {
        frappe.msgprint(__('Work Order created: {0}', [r.message]));
      });
    }, __('Actions'));
  }
});

frappe.ui.form.on('Prototype', {
  refresh(frm) {
    frm.add_custom_button('Open Clarinet Editor', () => {
      frappe.set_route('clarinet-editor', { prototype: frm.doc.name });
    }, __('Actions'));
  }
});
