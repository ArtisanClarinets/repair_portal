// File: repair_portal/repair_portal/instrument_setup/doctype/clarinet_setup_task/clarinet_setup_task_list.js
// Purpose: Better list view with indicators and smart filtering.
// Notes: Gantt view is built-in for doctypes with exp_start_date/exp_end_date.

frappe.listview_settings['Clarinet Setup Task'] = {
  add_fields: ['status', 'progress', 'exp_start_date', 'exp_end_date', 'priority', 'clarinet_initial_setup'],
  get_indicator(doc) {
    if (doc.status === 'Completed') return [__('Completed'), 'green', 'status,=,Completed'];
    if (doc.status === 'Pending Review') return [__('Pending Review'), 'orange', 'status,=,Pending Review'];
    if (doc.status === 'Working') return [__('Working'), 'blue', 'status,=,Working'];
    if (doc.status === 'Paused') return [(__('Paused')), 'grey', 'status,=,Paused'];
    if (doc.status === 'Canceled') return [__('Canceled'), 'red', 'status,=,Canceled'];
    return [__('Open'), 'yellow', 'status,=,Open'];
  },
  onload(listview) {
    // Apply filter from route_options if provided (e.g., from parent "View Tasks" button)
    if (frappe.route_options && frappe.route_options.clarinet_initial_setup) {
      listview.filter_area.add(['Clarinet Setup Task', 'clarinet_initial_setup', '=', frappe.route_options.clarinet_initial_setup]);
      // Clear route options so it doesn't linger
      frappe.route_options = null;
    }

    // Quick filters
    listview.page.add_inner_button(__('My Open Tasks'), () => {
      listview.filter_area.clear();
      listview.filter_area.add(['Clarinet Setup Task', 'status', '!=', 'Completed']);
      listview.filter_area.add(['Clarinet Setup Task', 'assigned_to', '=', frappe.session.user]);
      listview.run();
    });

    listview.page.add_inner_button(__('Due This Week'), () => {
      listview.filter_area.clear();
      listview.filter_area.add(['Clarinet Setup Task', 'exp_end_date', 'between', [frappe.datetime.week_start(), frappe.datetime.week_end()]]);
      listview.run();
    });
  }
};
