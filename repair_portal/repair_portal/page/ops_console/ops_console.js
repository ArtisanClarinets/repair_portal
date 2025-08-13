frappe.provide("your_app.pages.ops_console");

frappe.pages['ops-console'].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Operations Console',
    single_column: true
  });

  // Filters + actions
  const filter_group = new frappe.ui.FieldGroup({
    fields: [
      { fieldtype: 'Section Break', label: 'Filters' },
      { fieldname: 'from_date', label: 'From', fieldtype: 'Date', reqd: 1, default: frappe.datetime.month_start() },
      { fieldname: 'to_date', label: 'To', fieldtype: 'Date', reqd: 1, default: frappe.datetime.month_end() },
      { fieldname: 'customer', label: 'Customer', fieldtype: 'Link', options: 'Customer' },
      { fieldtype: 'Column Break' },
      { fieldname: 'refresh', label: 'Refresh', fieldtype: 'Button' },

      { fieldtype: 'Section Break', label: 'Quick Actions' },
      { fieldname: 'qa_customer', label: 'Customer', fieldtype: 'Link', options: 'Customer' },
      { fieldname: 'qa_item', label: 'Item', fieldtype: 'Link', options: 'Item' },
      { fieldname: 'qa_qty', label: 'Qty', fieldtype: 'Float', default: 1 },
      { fieldname: 'qa_rate', label: 'Rate', fieldtype: 'Currency' },
      { fieldtype: 'Column Break' },
      { fieldname: 'create_so', label: 'Create Sales Order', fieldtype: 'Button' },

      { fieldtype: 'Section Break', label: 'Quick ToDo' },
      { fieldname: 'todo_subject', label: 'Subject', fieldtype: 'Data' },
      { fieldname: 'todo_due', label: 'Due Date', fieldtype: 'Date' },
      { fieldtype: 'Column Break' },
      { fieldname: 'create_todo', label: 'Add ToDo', fieldtype: 'Button' },
    ],
    body: $(page.body),
  });
  filter_group.make();

  // Containers
  const list_container = $('<div class="ops-list" style="margin-top: 1rem;"></div>').appendTo(page.body);
  const msg = frappe.msgprint; // handy alias

  // Handlers
  filter_group.get_field('refresh').$input.on('click', load_sales_orders);
  filter_group.get_field('create_so').$input.on('click', create_sales_order);
  filter_group.get_field('create_todo').$input.on('click', create_todo);

  // Initial load
  load_sales_orders();

  function get_filters() {
    const v = filter_group.get_values();
    if (!v) return null;
    return {
      from_date: v.from_date,
      to_date: v.to_date,
      customer: v.customer || null,
    };
  }

  async function load_sales_orders() {
    const f = get_filters();
    if (!f) return;
    list_container.empty().text('Loading...');
    try {
      const data = await frappe.xcall('your_app.api.ops_console_get_sales_orders', f);
      render_table(data || []);
    } catch (e) {
      list_container.empty();
      frappe.msgprint({message: e.message || e, indicator: 'red', title: 'Failed to load'});
    }
  }

  function render_table(rows) {
    list_container.empty();

    if (!rows.length) {
      list_container.text('No Sales Orders in range.');
      return;
    }

    // Simple table (keeps deps minimal). Swap with frappe.DataTable if you prefer.
    const tbl = $(`
      <table class="table table-bordered">
        <thead>
          <tr>
            <th>SO</th><th>Customer</th><th>Transaction Date</th><th>Grand Total</th><th>Status</th><th>Open</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    `);
    rows.forEach(r => {
      const link = `<a href="/app/sales-order/${r.name}">Open</a>`;
      const tr = $(`
        <tr>
          <td>${frappe.utils.escape_html(r.name)}</td>
          <td>${frappe.utils.escape_html(r.customer || '')}</td>
          <td>${frappe.datetime.str_to_user(r.transaction_date)}</td>
          <td>${format_currency(r.grand_total, r.currency || frappe.defaults.get_default('currency'))}</td>
          <td>${frappe.utils.escape_html(r.status || '')}</td>
          <td>${link}</td>
        </tr>
      `);
      tbl.find('tbody').append(tr);
    });
    list_container.append(tbl);
  }

  async function create_sales_order() {
    const v = filter_group.get_values();
    if (!v.qa_customer || !v.qa_item || !v.qa_qty) {
      frappe.msgprint('Customer, Item and Qty are required.');
      return;
    }
    try {
      const so_name = await frappe.xcall('your_app.api.ops_console_make_sales_order', {
        customer: v.qa_customer,
        item_code: v.qa_item,
        qty: v.qa_qty,
        rate: v.qa_rate
      });
      frappe.show_alert({message: `Sales Order ${so_name} created`, indicator: 'green'});
      load_sales_orders();
      frappe.set_route('Form', 'Sales Order', so_name);
    } catch (e) {
      frappe.msgprint({message: e.message || e, indicator: 'red', title: 'Failed to create Sales Order'});
    }
  }

  async function create_todo() {
    const v = filter_group.get_values();
    if (!v.todo_subject) {
      frappe.msgprint('Subject is required.');
      return;
    }
    try {
      const name = await frappe.xcall('your_app.api.ops_console_make_todo', {
        subject: v.todo_subject,
        date: v.todo_due
      });
      frappe.show_alert({message: `ToDo ${name} added`, indicator: 'green'});
      filter_group.set_value('todo_subject', '');
      filter_group.set_value('todo_due', '');
    } catch (e) {
      frappe.msgprint({message: e.message || e, indicator: 'red', title: 'Failed to add ToDo'});
    }
  }
};
