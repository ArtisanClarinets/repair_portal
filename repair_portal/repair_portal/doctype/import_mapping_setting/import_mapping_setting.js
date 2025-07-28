frappe.ui.form.on('Import Mapping Setting', {
  onload(frm) {
    // If doctype already set, fetch its fields
    if (frm.is_new()) return;
    if (frm.doc.target_doctype) {
      frm.trigger('target_doctype');
    }
  },

  target_doctype(frm) {
    const dt = frm.doc.target_doctype;
    if (!dt) {
      frm.clear_table('child_mapping');
      return frm.refresh_field('child_mapping');
    }

    frm.toggle_enable('target_doctype', false);
    frm.set_df_property('child_mapping', 'read_only', 1);
    frappe.show_progress(__('Loading Fields…'), 1, 2);

    frappe.call({
      method: 'repair_portal.repair_portal.doctype.import_mapping_setting.import_mapping_setting.get_fields_for_doctype',
      args: { doctype: dt },
      freeze: true,
      callback: function(r) {
        frappe.hide_progress();
        if (r.exc) {
          frappe.msgprint({ title: __('Error'), message: r.exc, indicator: 'red' });
          return;
        }
        populate_mappings(frm, r.message);
      }
    });
  }
});

function populate_mappings(frm, fields) {
  frm.clear_table('child_mapping');
  fields.forEach((f, idx) => {
    let row = frm.add_child('child_mapping');
    row.idx = idx;
    row.field_name = f.fieldname;
    row.source_label = f.label;
    row.required_field = f.reqd === 1;
  });
  frm.refresh_field('child_mapping');
  frappe.msgprint({ message: __('{0} fields loaded.', [fields.length]), indicator: 'green' });
}
