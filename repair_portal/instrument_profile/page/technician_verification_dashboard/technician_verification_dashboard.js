// Path: instrument_profile/page/technician_verification_dashboard/technician_verification_dashboard.js
// Date: 2025-06-15
// Version: 1.0
// Purpose: Client-side logic for the technician verification dashboard to validate client-submitted instrument profiles.

frappe.pages['technician_verification_dashboard'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Technician Verification Dashboard',
        single_column: true
    });

    page.add_inner_button('Refresh', () => {
        load_dashboard_content(page);
    });

    load_dashboard_content(page);
};

function load_dashboard_content(page) {
    frappe.call({
        method: 'repair_portal.instrument_profile.page.technician_verification_dashboard.technician_verification_dashboard.get_pending_profiles',
        callback: function(r) {
            if (r.message && r.message.length) {
                let html = '<table class="table table-bordered"><thead><tr><th>Instrument</th><th>Client</th><th>Status</th><th>Actions</th></tr></thead><tbody>';
                r.message.forEach(profile => {
                    html += `<tr>
                        <td>${profile.name}</td>
                        <td>${profile.client}</td>
                        <td>${profile.status}</td>
                        <td><button class='btn btn-sm btn-primary' onclick='verifyInstrument("${profile.name}")'>Verify</button></td>
                    </tr>`;
                });
                html += '</tbody></table>';
                page.main.html(html);
            } else {
                page.main.html('<p class="text-muted">No pending instrument profiles.</p>');
            }
        }
    });
}

function verifyInstrument(name) {
    frappe.call({
        method: 'repair_portal.instrument_profile.page.technician_verification_dashboard.technician_verification_dashboard.verify_instrument',
        args: { name },
        callback: function() {
            frappe.show_alert({ message: 'Instrument verified.', indicator: 'green' });
            frappe.pages['technician_verification_dashboard'].on_page_load(frappe.container.page.wrapper);
        }
    });
}