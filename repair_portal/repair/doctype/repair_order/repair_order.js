// -*- coding: utf-8 -*-
// Relative Path: repair_portal/repair/doctype/repair_order/repair_order.js
// Version: 2.3.0 (2025-09-17)
// Purpose:
//   Client-side UX for Repair Order:
//     - "Create" shortcuts for stage documents
//     - Integration actions:
//         * Create Material Issue (from Planned)  -> drafts Stock Entry prefilled from planned_materials
//         * Create Material Issue (Actuals)       -> drafts a blank Stock Entry (user adds items)
//         * Refresh Actuals from Stock Entry      -> mirrors submitted SE items into RO.actual_materials
//         * Generate Sales Invoice                 -> parts (actuals) + labor (minutes→hours)
//   - Visual cues for workflow and warranty
//
// Requirements (whitelisted methods in repair_order.py):
//   - create_material_issue_draft(repair_order, include_planned=0|1)
//   - generate_sales_invoice_from_ro(repair_order)
//   - refresh_actuals_from_stock_entry(repair_order, stock_entry)

frappe.ui.form.on("Repair Order", {
  refresh(frm) {
    if (!frm.is_new()) {
      add_status_badges(frm);
      add_create_shortcuts(frm);
      add_integration_actions(frm);
    }
  },
});

// ---------------------------------------------------------------------------
// Visual: workflow & warranty badges
// ---------------------------------------------------------------------------
function add_status_badges(frm) {
  // Workflow state headline (read-only field)
  if (frm.doc.workflow_state) {
    frm.dashboard.set_headline(
      __("<b>Status:</b> {0}", [frappe.utils.escape_html(frm.doc.workflow_state)])
    );
  }

  // Warranty flag, if present on schema
  if ("is_warranty" in frm.doc) {
    const isW = cint(frm.doc.is_warranty);
    const until = frm.doc.warranty_until || "";
    const msg = isW
      ? __("Warranty: Active {0}", [until ? __("until {0}", [frappe.datetime.global_date_format(until)]) : ""])
      : __("Warranty: Not Active");
    frm.dashboard.add_comment(msg, isW ? "green" : "orange");
  }
}

// ---------------------------------------------------------------------------
// "Create" shortcuts
// ---------------------------------------------------------------------------
function add_create_shortcuts(frm) {
  const make = (label, doctype) => {
    frm.add_custom_button(
      label,
      () => {
        const opts = {
          repair_order: frm.doc.name,
          customer: frm.doc.customer,
          instrument_profile: frm.doc.instrument_profile,
        };
        frappe.new_doc(doctype, opts);
      },
      __("Create")
    );
  };

  make("Clarinet Intake", "Clarinet Intake");
  make("Instrument Inspection", "Instrument Inspection");
  make("Service Plan", "Service Plan");
  make("Repair Estimate", "Repair Estimate");
  make("Final QA Checklist", "Final QA Checklist");
  make("Measurement Session", "Measurement Session");
  make("Repair Task", "Repair Task");
}

// ---------------------------------------------------------------------------
// ERPNext Integration Actions
// ---------------------------------------------------------------------------
function add_integration_actions(frm) {
  // Pre-flight requirement check helper
  const ensure = (conds) => {
    const missing = [];
    Object.keys(conds).forEach((label) => {
      if (!conds[label]) missing.push(label);
    });
    if (missing.length) {
      frappe.msgprint({
        title: __("Missing Required Fields"),
        message: __("Please set: {0}", [missing.join(", ")]),
        indicator: "orange",
      });
      return false;
    }
    return true;
  };

  // 0) Create Material Issue (from Planned) — drafts SE with items prefilled from planned_materials
  frm.add_custom_button(
    __("Create Material Issue (from Planned)"),
    () => {
      if (!ensure({
        Company: frm.doc.company,
        "Source Warehouse": frm.doc.warehouse_source,
      })) {
        return;
      }
      const planned_rows = (frm.doc.planned_materials || []).filter(r => r.item_code && flt(r.qty) > 0);
      if (planned_rows.length === 0) {
        frappe.msgprint({
          title: __("No Planned Materials"),
          message: __("Add at least one Planned Material row with Item and Qty > 0."),
          indicator: "orange",
        });
        return;
      }

      frappe.call({
        method: "repair_portal.repair_portal.repair.doctype.repair_order.repair_order.create_material_issue_draft",
        args: { repair_order: frm.doc.name, include_planned: 1 },
        freeze: true,
        freeze_message: __("Creating Stock Entry draft from Planned Materials…"),
        callback: (r) => {
          if (r && r.message && r.message.length) {
            const se_name = r.message[0];
            frappe.show_alert({ message: __("Stock Entry draft created from Planned Materials."), indicator: "green" });
            frappe.set_route("Form", "Stock Entry", se_name);
          }
        },
        error: (err) => {
          console.error(err);
          frappe.msgprint({
            title: __("Error"),
            message: __("Could not create Stock Entry draft from Planned Materials."),
            indicator: "red",
          });
        },
      });
    },
    __("Actions")
  );

  // 1) Actuals flow: create a Stock Entry draft (Material Issue)
  frm.add_custom_button(
    __("Create Material Issue (Actuals)"),
    () => {
      if (!ensure({
        Company: frm.doc.company,
        "Source Warehouse": frm.doc.warehouse_source,
      })) {
        return;
      }
      frappe.call({
        method: "repair_portal.repair_portal.repair.doctype.repair_order.repair_order.create_material_issue_draft",
        args: { repair_order: frm.doc.name, include_planned: 0 },
        freeze: true,
        freeze_message: __("Creating Stock Entry draft…"),
        callback: (r) => {
          if (r && r.message && r.message.length) {
            const se_name = r.message[0];
            frappe.show_alert({
              message: __("Stock Entry draft created. Add item rows and include this RO in Remarks or line Descriptions for auto-linking."),
              indicator: "blue",
            });
            frappe.set_route("Form", "Stock Entry", se_name);
          }
        },
        error: (err) => {
          console.error(err);
          frappe.msgprint({
            title: __("Error"),
            message: __("Could not create Stock Entry draft. Check that Company and Source Warehouse are set on the Repair Order."),
            indicator: "red",
          });
        },
      });
    },
    __("Actions")
  );

  // 2) Generate Sales Invoice (parts from Actual Materials + labor)
  frm.add_custom_button(
    __("Generate Sales Invoice"),
    () => {
      if (!ensure({
        Customer: frm.doc.customer,
        "Labor Item (Service)": frm.doc.labor_item,
        Company: frm.doc.company || frappe.defaults.get_default("company"),
      })) {
        return;
      }
      frappe.call({
        method: "repair_portal.repair_portal.repair.doctype.repair_order.repair_order.generate_sales_invoice_from_ro",
        args: { repair_order: frm.doc.name },
        freeze: true,
        freeze_message: __("Generating Sales Invoice…"),
        callback: (r) => {
          if (r && r.message) {
            frappe.set_route("Form", "Sales Invoice", r.message);
          }
        },
        error: (err) => {
          console.error(err);
          frappe.msgprint({
            title: __("Error"),
            message: __("Could not generate Sales Invoice. Ensure Customer and Labor Item are set, and validate Actual Materials if needed."),
            indicator: "red",
          });
        },
      });
    },
    __("Actions")
  );

  // 3) Manual mirror: pull Actual Materials from a submitted Stock Entry
  frm.add_custom_button(
    __("Refresh Actuals from Stock Entry"),
    () => {
      frappe.prompt(
        [
          {
            fieldname: "stock_entry",
            label: __("Submitted Stock Entry"),
            fieldtype: "Link",
            options: "Stock Entry",
            reqd: 1,
          },
        ],
        (values) => {
          frappe.call({
            method: "repair_portal.repair_portal.repair.doctype.repair_order.repair_order.refresh_actuals_from_stock_entry",
            args: {
              repair_order: frm.doc.name,
              stock_entry: values.stock_entry,
            },
            freeze: true,
            freeze_message: __("Mirroring Stock Entry items into Actual Materials…"),
            callback: () => {
              frappe.show_alert({ message: __("Actual Materials updated from Stock Entry."), indicator: "green" });
              frm.reload_doc();
            },
            error: (err) => {
              console.error(err);
              frappe.msgprint({
                title: __("Error"),
                message: __("Could not mirror Actual Materials. Ensure the Stock Entry exists and is submitted."),
                indicator: "red",
              });
            },
          });
        },
        __("Mirror Actuals"),
        __("Mirror")
      );
    },
    __("Actions")
  );
}

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------
function cint(v) {
  try {
    return parseInt(v, 10) || 0;
  } catch (e) {
    return 0;
  }
}
function flt(v) {
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}
