// -*- coding: utf-8 -*-
// Absolute Path: /home/frappe/frappe-bench/apps/repair_portal/repair_portal/intake/doctype/clarinet_intake/clarinet_intake_list.js
// Last Updated: 2025-09-19
// Version: v1.0.0 (Desk UX: indicators, quick-filters, bulk actions, safe async)
// Purpose:
//   List/Desk enhancements for Clarinet Intake
//   • Clear status indicators (color + quick filter)
//   • One-click quick filters for Intake Type & common Statuses
//   • Bulk status updates with permission checks
//   • Convenience buttons to open Settings and related lists
//
// Notes:
//   • Uses only official Frappe ListView APIs (v15-compatible)
//   • No server-side customization required for quick filters/bulk updates
//   • If your status field uses Workflow, these client-side updates still respect permissions

(() => {
  const DOCTYPE = 'Clarinet Intake';

  // Color map for status (supports both "Awaiting Custom Approval" and "Awaiting Customer Approval")
  const STATUS_META = {
    Pending: { color: 'gray' },
    Received: { color: 'blue' },
    Inspection: { color: 'green' },
    Setup: { color: 'green' },
    Repair: { color: 'purple' },
    'Awaiting Custom Approval': { color: 'orange' },
    'Awaiting Customer Approval': { color: 'orange' },
    'Awaiting Payment': { color: 'yellow' },
    'In Transit': { color: 'light-blue' },
    'Repair Complete': { color: 'orange' },
    'Returned to Customer': { color: 'purple' },
  };

  // Utility: add/replace a single filter and refresh
  function set_single_filter(listview, fieldname, condition, value) {
    // remove existing filter on same field
    listview.filter_area.remove(fieldname);
    listview.filter_area.add([[DOCTYPE, fieldname, condition, value]]);
    listview.refresh();
  }

  // Utility: bulk status update with guardrails
  async function bulk_set_status(listview, new_status) {
    const names = listview.get_checked_items(true);
    if (!names.length) {
      frappe.show_alert({ message: __('Select at least one Intake first.'), indicator: 'orange' });
      return;
    }
    const confirmed = await frappe.confirm(
      __('Change status of {0} record(s) to <b>{1}</b>?', [names.length, new_status])
    );
    if (!confirmed) return;

    const results = await Promise.allSettled(
      names.map((name) =>
        frappe.call({
          method: 'frappe.client.set_value',
          args: { doctype: DOCTYPE, name, fieldname: 'status', value: new_status },
          freeze: false,
        })
      )
    );

    const ok = results.filter((r) => r.status === 'fulfilled').length;
    const failed = results.length - ok;
    if (ok) frappe.show_alert({ message: __('{0} updated', [ok]), indicator: 'green' });
    if (failed) frappe.msgprint({
      title: __('Some updates failed'),
      message: __('{0} record(s) could not be updated. Check permissions or workflow.', [failed]),
      indicator: 'red',
    });
    listview.refresh();
  }

  // Utility: Add a grouped quick-filter button
  function add_quick_filter_button(listview, group_label, label, cb) {
    listview.page.add_inner_button(__(label), cb, __(group_label));
  }

  frappe.listview_settings[DOCTYPE] = {
    // Fetch these extra fields to avoid additional queries in get_indicator/formatters
    add_fields: ['status', 'intake_type', 'manufacturer', 'serial_no', 'customer'],
    hide_name_column: false,
    order_by: 'modified desc',

    // Color indicators for each row based on status
    get_indicator: function (doc) {
      const meta = STATUS_META[doc.status] || { color: 'gray' };
      // The third element is the filter that will be applied when the indicator is clicked
      return [__(doc.status || 'Unknown'), meta.color, ['status', '=', doc.status]];
    },

    // Optional formatting tweaks
    formatters: {
      serial_no: function (value) {
        if (!value) return value;
        return `<span style="font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;">${frappe.utils.escape_html(value)}</span>`;
      },
    },

    // Called once when the list is loaded
    onload(listview) {
      // ---------- Quick Filters: Intake Type ----------
      add_quick_filter_button(listview, 'Type', 'New Inventory', () =>
        set_single_filter(listview, 'intake_type', '=', 'New Inventory')
      );
      add_quick_filter_button(listview, 'Type', 'Repair', () =>
        set_single_filter(listview, 'intake_type', '=', 'Repair')
      );
      add_quick_filter_button(listview, 'Type', 'Maintenance', () =>
        set_single_filter(listview, 'intake_type', '=', 'Maintenance')
      );

      // ---------- Quick Filters: Status ----------
      ['Received', 'Inspection', 'Repair', 'Repair Complete', 'Returned to Customer'].forEach(
        (status) => {
          add_quick_filter_button(listview, 'Status', status, () =>
            set_single_filter(listview, 'status', '=', status)
          );
        }
      );

      // ---------- Quick Filters: Today / This Week ----------
      add_quick_filter_button(listview, 'Dates', 'Today', () => {
        listview.filter_area.remove('intake_date');
        listview.filter_area.add([[DOCTYPE, 'intake_date', 'Timespan', 'Today']]);
        listview.refresh();
      });
      add_quick_filter_button(listview, 'Dates', 'This Week', () => {
        listview.filter_area.remove('intake_date');
        listview.filter_area.add([[DOCTYPE, 'intake_date', 'Timespan', 'This Week']]);
        listview.refresh();
      });

      // ---------- Convenience: Open Settings / Related ----------
      listview.page.add_inner_button(__('Settings'), () => {
        frappe.set_route('Form', 'Clarinet Intake Settings');
      }, __('Actions'));

      listview.page.add_inner_button(__('Instrument Inspections'), () => {
        frappe.set_route('List', 'Instrument Inspection');
      }, __('Actions'));

      listview.page.add_inner_button(__('Initial Setups'), () => {
        frappe.set_route('List', 'Clarinet Initial Setup');
      }, __('Actions'));

      // ---------- Bulk Actions: Status ----------
      listview.page.add_actions_menu_item(__('Mark as Received'), () =>
        bulk_set_status(listview, 'Received')
      );
      listview.page.add_actions_menu_item(__('Move to Inspection'), () =>
        bulk_set_status(listview, 'Inspection')
      );
      listview.page.add_actions_menu_item(__('Move to Repair'), () =>
        bulk_set_status(listview, 'Repair')
      );
      listview.page.add_actions_menu_item(__('Mark Repair Complete'), () =>
        bulk_set_status(listview, 'Repair Complete')
      );
      listview.page.add_actions_menu_item(__('Mark Returned to Customer'), () =>
        bulk_set_status(listview, 'Returned to Customer')
      );

      // ---------- Suggested list columns (informational) ----------
      // Users can still customize columns via List Settings; below is just documentation/comment:
      // Proposed columns: intake_record_id (Title), status, intake_type, serial_no, manufacturer, model, customer, modified
    },

    // Default filter set (can be changed by the user and persists via route)
    filters: [
      // Example: only open-ish statuses by default; comment/uncomment to taste
      // ['Clarinet Intake', 'status', 'not in', ['Returned to Customer']],
    ],
  };
})();
