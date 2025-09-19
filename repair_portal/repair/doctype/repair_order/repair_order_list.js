// Path: repair_portal/public/js/listviews/repair_order_list.js
// Purpose: Color indicators for SLA status on Repair Orders and quick columns

frappe.listview_settings["Repair Order"] = {
  add_fields: ["sla_status", "sla_progress_pct", "sla_due", "sla_breached"],
  get_indicator(doc) {
    // Map SLA status to colors
    const status = (doc.sla_status || "None").toLowerCase();
    if (status === "green") {
      return [__("SLA Green"), "green", "sla_status,=,Green"];
    }
    if (status === "yellow") {
      return [__("SLA Yellow"), "orange", "sla_status,=,Yellow"];
    }
    if (status === "red") {
      return [__("SLA Red"), "red", "sla_status,=,Red"];
    }
    return [__("No SLA"), "grey", "sla_status,=,None"];
  },
  onload(listview) {
    // Add common SLA filters for convenience
    listview.page.add_inner_button(__("SLA Breached"), () => {
      listview.filter_area.add([[ "Repair Order", "sla_breached", "=", "1" ]]);
      listview.refresh();
    });

    listview.page.add_inner_button(__("Due Today"), () => {
      const today = frappe.datetime.get_today();
      listview.filter_area.add([
        [ "Repair Order", "sla_due", "Between", [today + " 00:00:00", today + " 23:59:59"] ],
      ]);
      listview.refresh();
    });
  },
};
