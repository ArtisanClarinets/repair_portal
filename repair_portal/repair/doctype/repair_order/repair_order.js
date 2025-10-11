frappe.provide("repair_portal.repair.repair_order");

const SLA_BADGE_COLOR = {
  "On Track": "green",
  "At Risk": "orange",
  "Paused": "blue",
  "Breached": "red",
};

frappe.ui.form.on("Repair Order", {
  refresh(frm) {
    set_dashboard(frm);
    register_workflow_buttons(frm);
    register_action_buttons(frm);
  },
});

function set_dashboard(frm) {
  if (!frm.doc.workflow_state) {
    return;
  }
  const state = frappe.utils.escape_html(frm.doc.workflow_state);
  frm.dashboard.set_headline(__("<b>State:</b> {0}", [state]));

  if (frm.doc.sla_status) {
    const badge = SLA_BADGE_COLOR[frm.doc.sla_status] || "blue";
    frm.dashboard.add_comment(
      __("SLA {0}", [frappe.utils.escape_html(frm.doc.sla_status)]),
      badge
    );
  }

  if (frm.doc.billing_status) {
    frm.dashboard.add_comment(
      __("Billing: {0}", [frappe.utils.escape_html(frm.doc.billing_status)]),
      frm.doc.billing_status === "Paid" ? "green" : "orange"
    );
  }

  if (frm.doc.total_billable_hours) {
    frm.dashboard.add_indicator(
      __("Labor Hours: {0}", [frm.doc.total_billable_hours]),
      "blue"
    );
  }

  if (frm.doc.qa_status) {
    const qaColor = frm.doc.qa_status === "Pass" ? "green" : frm.doc.qa_status === "Fail" ? "red" : "orange";
    frm.dashboard.add_indicator(
      __("QA: {0}", [frappe.utils.escape_html(frm.doc.qa_status)]),
      qaColor
    );
  }
}

function register_workflow_buttons(frm) {
  if (frm.is_new()) {
    return;
  }
  const state = frm.doc.workflow_state || "Requested";

  const add = (label, target) => {
    frm.add_custom_button(
      label,
      () => update_state(frm, target),
      __("Workflow")
    );
  };

  if (state === "Requested") {
    add(__("Mark Quoted"), "Quoted");
  }
  if (state === "Quoted") {
    add(__("Start Work"), "In Progress");
  }
  if (state === "In Progress") {
    add(__("Send to QA"), "Ready for QA");
  }
  if (state === "Ready for QA") {
    add(__("Complete"), "Completed");
    add(__("Reopen"), "In Progress");
  }
  if (state === "Completed") {
    add(__("Deliver"), "Delivered");
  }
}

function update_state(frm, target) {
  frappe.call({
    method: 'frappe.client.set_value',
    args: {
      doctype: frm.doc.doctype,
      name: frm.doc.name,
      fieldname: 'workflow_state',
      value: target,
    },
    freeze: true,
    freeze_message: __("Updating state…"),
    callback: () => frm.reload_doc(),
  });
}

function register_action_buttons(frm) {
  if (frm.is_new()) {
    return;
  }
  frm.add_custom_button(
    __("Consume Materials"),
    () => {
      frm.call({
        method: 'consume_materials',
        freeze: true,
        freeze_message: __("Creating Stock Entry…"),
        callback: (r) => {
          if (r.message) {
            frappe.show_alert({
              message: __("Stock Entry {0} created", [r.message]),
              indicator: "green",
            });
            frm.reload_doc();
          }
        },
      });
    },
    __("Actions")
  );

  frm.add_custom_button(
    __("Generate Invoice"),
    () => {
      frm.call({
        method: 'make_sales_invoice',
        freeze: true,
        freeze_message: __("Creating Sales Invoice…"),
        callback: (r) => {
          if (r.message) {
            frappe.show_alert({
              message: __("Sales Invoice {0} created", [r.message]),
              indicator: "green",
            });
          }
        },
      });
    },
    __("Actions")
  );

  if (frm.doc.sla_status !== "Paused") {
    frm.add_custom_button(
      __("Pause SLA"),
      () => {
        frappe.prompt(
          {
            label: __("Reason"),
            fieldtype: "Small Text",
            fieldname: "reason",
            reqd: 1,
          },
          (values) => {
            frappe.call({
              method: "repair_portal.repair.doctype.repair_order.repair_order.pause_sla",
              args: { order: frm.doc.name, reason: values.reason },
              freeze: true,
              freeze_message: __("Pausing SLA…"),
              callback: () => frm.reload_doc(),
            });
          },
          __("Pause SLA")
        );
      },
      __("Actions")
    );
  } else {
    frm.add_custom_button(
      __("Resume SLA"),
      () => {
        frappe.call({
          method: "repair_portal.repair.doctype.repair_order.repair_order.resume_sla",
          args: { order: frm.doc.name },
          freeze: true,
          freeze_message: __("Resuming SLA…"),
          callback: () => frm.reload_doc(),
        });
      },
      __("Actions")
    );
  }
}
