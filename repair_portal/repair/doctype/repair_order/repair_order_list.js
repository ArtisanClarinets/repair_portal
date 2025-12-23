// Path: repair_portal/public/js/listviews/repair_order_list.js
// Purpose: Color indicators for SLA status on Repair Orders and quick columns

frappe.listview_settings["Repair Order"] = {
  add_fields: ["sla_status", "sla_progress_pct", "sla_due", "sla_breached"],
  get_indicator(doc) {
    // Map SLA status to colors and icons for accessibility
    const status = (doc.sla_status || "None").toLowerCase();
    const get_label = (icon_name, text) => {
        return `
            <span class="indicator-label-with-icon">
                <svg class="icon icon-sm" style="margin-right: 4px;">
                    <use href="#icon-${icon_name}"></use>
                </svg>
                ${text}
            </span>
        `;
    }

    if (status === "green") {
      return [get_label("check", __("SLA Green")), "green", "sla_status,=,Green"];
    }
    if (status === "yellow") {
      return [get_label("warning", __("SLA Yellow")), "orange", "sla_status,=,Yellow"];
    }
    if (status === "red") {
      return [get_label("error", __("SLA Red")), "red", "sla_status,=,Red"];
    }
    return [get_label("info", __("No SLA")), "grey", "sla_status,=,None"];
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
