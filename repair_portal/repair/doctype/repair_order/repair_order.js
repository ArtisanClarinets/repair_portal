// Repair Order client: create-stage shortcuts & basic helpers

frappe.ui.form.on("Repair Order", {
  refresh(frm) {
    if (!frm.doc.__islocal) {
      add_create_buttons(frm);
    }
  },
});

function add_create_buttons(frm) {
  const make = (label, doctype) => {
    frm.add_custom_button(label, () => {
      const opts = {
        repair_order: frm.doc.name,
        customer: frm.doc.customer,
        instrument_profile: frm.doc.instrument_profile,
      };
      frappe.new_doc(doctype, opts);
    }, __("Create"));
  };

  make("Clarinet Intake", "Clarinet Intake");
  make("Instrument Inspection", "Instrument Inspection");
  make("Service Plan", "Service Plan");
  make("Repair Estimate", "Repair Estimate");
  make("Final QA Checklist", "Final QA Checklist");
  make("Measurement Session", "Measurement Session");
  make("Repair Task", "Repair Task");
}
