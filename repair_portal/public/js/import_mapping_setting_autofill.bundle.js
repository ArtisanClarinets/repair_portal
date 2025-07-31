// File: repair_portal/public/js/import_mapping_setting_autofill.js
frappe.ui.form.on("Import Mapping Setting", {
  target_doctype: function(frm) {
    // only run if they've chosen something
    if (frm.doc.target_doctype) {
      frm.call("populate_field_mappings")
        .then((r) => {
          // r.message is the new child_mapping list
          frm.refresh_fields("child_mapping");
        });
    }
  }
});