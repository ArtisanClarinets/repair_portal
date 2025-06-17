frappe.pages['technician-verification-dashboard'].on_page_load = function(wrapper) {
  let page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Technician Verification Dashboard',
    single_column: true
  });

  page.add_field({
    label: 'Filter by Brand',
    fieldname: 'brand_filter',
    fieldtype: 'Link',
    options: 'Brand',
    change() {
      load_instruments();
    }
  });

  let container = $('<div class="pending-instruments">').appendTo(page.body);

  async function load_instruments() {
    const brand = page.fields_dict.brand_filter.get_value();
    frappe.call({
      method: 'repair_portal.instrument_profile.page.technician_verification_dashboard.technician_verification_dashboard.get_pending_profiles',
      args: { brand },
      callback: function(r) {
        container.empty();
        if (!r.message || !r.message.length) {
          container.html('<p>No pending instruments.</p>');
          return;
        }
        r.message.forEach(row => {
          const item = $(`
            <div class="card mb-3">
              <div class="card-body">
                <h5>${row.name}</h5>
                <p><strong>Client:</strong> ${row.client}</p>
                <p><strong>Status:</strong> ${row.status}</p>
                <button class="btn btn-sm btn-success">Verify</button>
              </div>
            </div>
          `);
          item.find('button').on('click', () => {
            frappe.call({
              method: 'repair_portal.instrument_profile.page.technician_verification_dashboard.technician_verification_dashboard.verify_instrument',
              args: { name: row.name },
              callback: () => load_instruments()
            });
          });
          container.append(item);
        });
      }
    });
  }

  load_instruments();
};