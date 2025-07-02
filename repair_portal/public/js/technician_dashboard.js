frappe.pages['technician-dashboard'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Technician Dashboard'),
        single_column: true
    });

    $(wrapper).html(`
        <div class="dashboard-section">
            <div class="row" id="dashboard-cards"></div>
            <h4 class="mt-4">Recent Activity</h4>
            <div class="row" id="recent-activity"></div>
        </div>
    `);

    loadDashboardCounts();
    loadRecentActivity();
};

function loadDashboardCounts() {
    frappe.call({
        method: "repair_portal.api.dashboard.get_technician_dashboard_counts",
        callback: function(r) {
            if (r.message) {
                const counts = r.message;
                const container = $('#dashboard-cards');
                container.empty();
                Object.keys(counts).forEach(key => {
                    const label = frappe.utils.to_title(key.replace(/_/g, ' '));
                    const value = counts[key];
                    container.append(`
                        <div class="col-md-3 mb-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">${label}</h5>
                                    <p class="card-text display-4">${value}</p>
                                </div>
                            </div>
                        </div>
                    `);
                });
            }
        }
    });
}

function loadRecentActivity() {
    frappe.call({
        method: "repair_portal.api.dashboard.get_recent_activity",
        callback: function(r) {
            if (r.message) {
                const activity = r.message;
                const container = $('#recent-activity');
                container.empty();

                Object.keys(activity).forEach(section => {
                    container.append(`<h5 class="mt-3">${frappe.utils.to_title(section.replace(/_/g, ' '))}</h5>`);
                    let list = '<ul class="list-group mb-3">';
                    activity[section].forEach(item => {
                        list += `<li class="list-group-item">
                            <strong>${item.name}</strong>
                            <span class="badge badge-primary ml-2">${item.status || item.workflow_state || ''}</span>
                            <small class="text-muted float-right">${frappe.datetime.comment_when(item.modified)}</small>
                        </li>`;
                    });
                    list += '</ul>';
                    container.append(list);
                });
            }
        }
    });
}