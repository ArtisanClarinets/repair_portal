// File: instrument_profile/doctype/instrument_tracker/instrument_tracker.js
// Updated: 2025-06-14
// Version: 1.0
// Purpose: UI/JS logic for dashboard aggregation of Instrument Tracker.

frappe.ui.form.on('Instrument Tracker', {
    refresh(frm) {
        // Render service logs as dashboard table
        if (frm.doc.__onload && frm.doc.__onload.service_logs) {
            let logs = frm.doc.__onload.service_logs;
            frm.dashboard.add_section(
                frappe.render_template('instrument_tracker_service_logs', {logs: logs}),
                'Service/Repair Logs'
            );
        }
        // Render inspection logs as dashboard table
        if (frm.doc.__onload && frm.doc.__onload.inspection_logs) {
            let logs = frm.doc.__onload.inspection_logs;
            frm.dashboard.add_section(
                frappe.render_template('instrument_tracker_inspection_logs', {logs: logs}),
                'Inspection Logs'
            );
        }
    }
});

// Add templates (inline or via includes/templates folder as needed)
frappe.templates['instrument_tracker_service_logs'] = `
<table class="table table-bordered">
    <thead><tr>
        <th>Date</th><th>Type</th><th>Description</th><th>Performed By</th><th>Notes</th>
    </tr></thead>
    <tbody>
        {% for row in logs %}
        <tr>
            <td>{{ row.date }}</td>
            <td>{{ row.service_type }}</td>
            <td>{{ row.description }}</td>
            <td>{{ row.performed_by }}</td>
            <td>{{ row.notes }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
`;

frappe.templates['instrument_tracker_inspection_logs'] = `
<table class="table table-bordered">
    <thead><tr>
        <th>Date</th><th>Inspected By</th><th>Condition</th><th>Notes</th>
    </tr></thead>
    <tbody>
        {% for row in logs %}
        <tr>
            <td>{{ row.inspection_date }}</td>
            <td>{{ row.inspected_by }}</td>
            <td>{{ row.overall_condition }}</td>
            <td>{{ row.notes }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
`;
