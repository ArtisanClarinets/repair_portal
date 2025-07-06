// ─────────────────────────────────────────────────────────────────────────
// Clarinet Intake client script (v1.3.0 — 2025-07-07)
//   • sets defaults
//   • shows dashboard indicators
//   • single “Create / View Quality Inspection” flow
// ─────────────────────────────────────────────────────────────────────────

frappe.ui.form.on("Clarinet Intake", {
  // 1  onload -------------------------------------------------------------
  onload(frm) {
    frm.doc.intake_type ||= "Inventory";

    if (frm.doc.intake_type === "Inventory") {
      frm.doc.stock_status ||= "Inspection";
      if (!frm.doc.inspected_by && frappe.session.user !== "Guest") {
        frm.set_value("inspected_by", frappe.session.user);
      }
    } else {
      frm.doc.repair_status ||= "Pending";
    }
  },

  // 2  refresh ------------------------------------------------------------
  refresh(frm) {
    // force intake_type
    frm.doc.intake_type ||= "Inventory";

    if (
      frm.doc.intake_type === "Inventory" &&
      !frm.doc.inspected_by &&
      frappe.session.user !== "Guest"
    ) {
      frm.set_value("inspected_by", frappe.session.user);
    }

    // --- indicators ----------------------------------------------------
    frm.dashboard.clear_headline();
    frm.dashboard.clear_indicators();

    if (frm.doc.workflow_state) {
      frm.dashboard.add_indicator(
        __("Workflow: {0}", [frm.doc.workflow_state]),
        "blue"
      );
    }

    if (frm.doc.instrument_profile && !frm.is_new()) {
      frappe.show_alert(
        {
          message: __("Instrument Profile: {0}", [frm.doc.instrument_profile]),
          indicator: "green",
        },
        8
      );
    }

    // --- Quality Inspection buttons ------------------------------------
    if (frm.doc.quality_inspection) {
      frm.add_custom_button(
        __("View Quality Inspection"),
        () =>
          frappe.set_route("Form", "Quality Inspection", frm.doc.quality_inspection)
      );
    } else if (frm.doc.docstatus === 1 && frm.doc.intake_type === "Inventory") {
      frm.add_custom_button(
        __("Create Quality Inspection"),
        () => {
          frappe.call({
            method:
              "erpnext.stock.doctype.quality_inspection.quality_inspection.make_quality_inspection",
            args: {
              reference_type: "Clarinet Intake",
              reference_name: frm.doc.name,
              item_code: frm.doc.item_code,
              inspection_type: "Incoming",
            },
            callback({ message }) {
              if (message) {
                frappe.set_route("Form", "Quality Inspection", message);
              }
            },
          });
        }
      );
    }
  },

  // 3  intake_type change -------------------------------------------------
  intake_type(frm) {
    const isRepair = frm.doc.intake_type === "Repair";

    frm.toggle_reqd(["purchase_order", "warehouse"], !isRepair);
    frm.toggle_reqd(["customer", "due_date"], isRepair);

    if (isRepair) {
      frm.doc.repair_status ||= "Pending";
    } else {
      frm.doc.stock_status ||= "Inspection";
      if (!frm.doc.inspected_by && frappe.session.user !== "Guest") {
        frm.set_value("inspected_by", frappe.session.user);
      }
    }
  },

  // 4  validate -----------------------------------------------------------
  validate(frm) {
    if (frm.doc.checklist?.length) {
      const incomplete = frm.doc.checklist.filter((row) => row.status !== "Completed");
      if (incomplete.length) {
        frappe.throw(
          __("All accessories must be marked completed. Incomplete: {0}", [
            incomplete.map((r) => r.accessory || r.item).join(", "),
          ])
        );
      }
    }

    if (frm.doc.intake_type === "Repair" && !frm.doc.customer) {
      frappe.throw(__("Customer is required for Repair intake type."));
    }
  },

  // 5  workflow_state change ---------------------------------------------
  workflow_state(frm) {
    if (frm.doc.workflow_state === "Flagged") {
      frappe.prompt(
        [
          {
            label: __("Escalation Reason"),
            fieldname: "flagged_reason",
            fieldtype: "Small Text",
            reqd: 1,
          },
        ],
        (values) => {
          frm.set_value("flagged_reason", values.flagged_reason);
          frappe.msgprint(
            __("Reason captured. Escalation will be logged and managers notified.")
          );
        },
        __("Flag Intake"),
        __("Submit")
      );
    }
  },
});