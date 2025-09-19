// Path: repair_portal/repair/report/sla_compliance/sla_compliance.js
/* eslint-disable */

frappe.query_reports["SLA Compliance"] = {
  "filters": [
    {
      "fieldname": "from_date",
      "label": __("From Date"),
      "fieldtype": "Date"
    },
    {
      "fieldname": "to_date",
      "label": __("To Date"),
      "fieldtype": "Date"
    },
    {
      "fieldname": "workshop",
      "label": __("Workshop"),
      "fieldtype": "Link",
      "options": "Workshop"
    },
    {
      "fieldname": "service_type",
      "label": __("Service Type"),
      "fieldtype": "Data"
    },
    {
      "fieldname": "breached_only",
      "label": __("Breached Only"),
      "fieldtype": "Check",
      "default": 0
    }
  ]
};
